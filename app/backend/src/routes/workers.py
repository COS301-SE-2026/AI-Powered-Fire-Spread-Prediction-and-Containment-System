# for volunteer gpus
import asyncio
from datetime import datetime, timezone
import json
import logging
import os
from typing import Annotated, Dict, Optional

from fastapi import (APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status)
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.dependencies.auth import get_current_user
from app.backend.src.models.users import User
from app.backend.src.models.workers import WorkerNode
from app.backend.src.schemas.workers import WorkerRegisterRequest, WorkerTokenResponse
from app.backend.src.services import workers as worker_service

log = logging.getLogger("workers_route")

router = APIRouter(prefix="/api/v1/workers", tags=["Workers"])

# worker_id -> WebSocket
active_worker_connections: Dict[str, WebSocket] = {}

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
JOB_TIMEOUT_SECONDS = float(os.getenv("SIMULATION_JOB_TIMEOUT", "90.0"))


async def verify_worker_token(token: str) -> str:
    """Decodes and validates scoped Worker Device JWT.
    Returns and worker_id."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        worker_id: Optional[str] = payload.get("sub")
        role: Optional[str] = payload.get("role")
        token_type: Optional[str] = payload.get("type")

        if not worker_id or role != "worker_node" or token_type != "worker_device":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid worker credentials or scope",
            )
        return worker_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate worker credentails",
        )


@router.post("/keys", status_code=status.HTTP_201_CREATED)
def generate_worker_enrollment_key(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Generates a single-use setup key for the authenticated user and caches it in Valkey."""
    return worker_service.generate_worker_key(current_user.id)


@router.post(
    "/register",
    response_model=WorkerTokenResponse,
    status_code=status.HTTP_200_OK,
)
def register_worker(
    register_data: WorkerRegisterRequest,
    db: Annotated[Session, Depends(get_db)],
):
    """Verifies hardware specs, 
    burns Valkey setup key,
    persists node in db,
    issues the Worker Device JWT."""
    return worker_service.register_worker_node(db, register_data)


@router.websocket("/connect")
async def websocket_worker_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Persistent outbound WebSocket control-plane tunnel for volunteer worker nodes.
    Authenticates via the Worker Device JWT passed as a query param or auth header."""
    # extract token
    auth_token = token
    if not auth_token:
        auth_header = websocket.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            auth_token = auth_header.split(" ")[1]

    if not auth_token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        worker_id = await verify_worker_token(auth_token)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # verify worker existence active status
    node = db.query(WorkerNode).filter(WorkerNode.id == worker_id).first()
    if not node or node.status in ["rejected", "removed", "deactivated"]:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if node.status == "quarantined" and node.quarentine_until > datetime.now(timezone.utc):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    active_worker_connections[worker_id] = websocket

    node.status = "active"
    node.last_heartbeat = datetime.now(timezone.utc)
    db.commit()

    valkey = worker_service.valkey_client
    valkey.sadd("worker:pool:idle", worker_id)
    valkey.srem("worker:pool:busy", worker_id)

    log.info("Worker node %s connected and added to idle pool.", worker_id)

    try:
        while True:
            # heartbeat message listener loop
            try:
                raw_message = await asyncio.wait_for(websocket.receive_text(), timeout=20.0)
                data = json.loads(raw_message)
                msg_type = data.get("type")

                if msg_type == "pong" or msg_type == "ping":
                    node.last_heartbeat = datetime.now(timezone.utc)
                    db.commit()
                    if msg_type == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                    continue

                # completed simulation
                if msg_type == "simulation_result":
                    job_id = data.get("job_id")
                    log.info("Received simulation result for job %s from worker %s", job_id, worker_id)
                    # to dispatcher
                    valkey.setex(f"worker:sim:result:{job_id}", 60, json.dumps(data.get("payload", {})))
                    # return to idle
                    node.status = "active"
                    db.commit()
                    valkey.srem("worker:pool:busy", worker_id)
                    valkey.sadd("worker:pool:idle", worker_id)
                    continue

                # sim error
                if msg_type == "simulation_error":
                    job_id = data.get("job_id")
                    log.error("Worker %s failed simulation job %s: %s", worker_id, job_id, data.get("error"))
                    node.consecutive_failures += 1
                    node.status = "quarantined"
                    db.commit()
                    valkey.srem("worker:pool:busy", worker_id)
                    valkey.srem("worker:pool:idle", worker_id)
                    continue

            except asyncio.TimeoutError:
                # test socket alive
                try:
                    await websocket.send_text(json.dumps({"type": "ping"}))
                except Exception:
                    break

    except (WebSocketDisconnect, Exception) as err:
        log.warning("WebSocket connection dropped for worker %s: %s", worker_id, err)
    finally:
        active_worker_connections.pop(worker_id, None)
        valkey.srem("worker:pool:idle", worker_id)
        valkey.srem("worker:pool:busy", worker_id)

        try:
            node = db.query(WorkerNode).filter(WorkerNode.id == worker_id).first()
            if node and node.status not in ["quarantined", "removed", "deactivated"]:
                node.status = "offline"
                db.commit()
        except Exception as cleanup_err:
            log.error("Failed to update status for disconnected worker %s: %s", worker_id, cleanup_err)


async def dispatch_simulation_task(task_payload: dict, db: Session) -> dict:
    valkey = worker_service.valkey_client
    worker_id = valkey.spop("worker:pool:idle")

    if not worker_id:
        log.warning("No idle volunteer workers available.")
        return {"dispatched_to": "cloud_fallback", "status": "queued"}

    ws = active_worker_connections.get(worker_id)
    if not ws:
        valkey.srem("worker:pool:idle", worker_id)
        return {"dispatched_to": "cloud_fallback", "status": "queued"}

    job_id = task_payload.get("job_id", "sim_job")
    valkey.sadd("worker:pool:busy", worker_id)

    node = db.query(WorkerNode).filter(WorkerNode.id == worker_id).first()
    if node:
        node.status = "busy"
        db.commit()

    message = {
        "type": "simulation_job",
        "payload": task_payload,
    }

    try:
        await ws.send_text(json.dumps(message))

        result_key = f"worker:sim:result:{job_id}"
        elapsed = 0.0
        poll_interval = 0.5

        while elapsed < JOB_TIMEOUT_SECONDS:
            raw_reslult = valkey.get(result_key)
            if raw_reslult:
                valkey.delete(result_key)
                return json.loads(raw_reslult)

            if worker_id not in active_worker_connections:
                log.error("Worker %s disconnected mid-simulation for jab %s.", worker_id, job_id)
                break

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        log.warning("Worker %s exceeded 10s SLA limit on job %s. Quarantining", worker_id, JOB_TIMEOUT_SECONDS, job_id)
        if node:
            node.consecutive_failures += 1
            node.status = "quarantined"
            db.commit()
        valkey.srem("worker:pool:busy", worker_id)

    except Exception as err:
        log.error("Error communicating with worker %s on job %s: %s", worker_id, job_id, err)
        if node:
            node.consecutive_failures += 1
            node.status = "quarantined"
            db.commit()
        valkey.srem("worker:pool:busy", worker_id)

    return {"dispatched_to": "cloud_fallback", "status": "queued"}

