# for volunteer gpus
import asyncio
from datetime import datetime, timezone
import json
import logging
import os
from typing import Annotated, Dict, Optional, List

from fastapi import (APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status)
from jose import JWTError, jwt
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.dependencies.auth import get_current_user
from app.backend.src.models.users import User
from app.backend.src.models.workers import WorkerNode
from app.backend.src.schemas.workers import WorkerRegisterRequest, WorkerTokenResponse, ComputeDistrubutionRatio, WorkerNodeResponse, WorkerRemovalRequest, WorkerEnrollmentKeyResponse, WorkerEnrollmentKeyRequest
from app.backend.src.services import workers as worker_service
from app.backend.src.enums.user_role import UserRole

log = logging.getLogger("workers_route")

router = APIRouter(prefix="/api/v1/workers", tags=["Workers"])

db_session = Annotated[Session, Depends(get_db)]
current_active_user = Annotated[User, Depends(get_current_user)]

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


@router.get("", response_model=List[WorkerNodeResponse])
def get_workers(
    db: db_session,
    current_user: current_active_user,
):
    """List worker nodes. 
    Returns all nodes for admins or only the user's machines for volunteers."""
    is_admin = current_user.role == UserRole.admin
    return worker_service.list_workers(
        db=db,
        user_id=current_user.id,
        is_admin=is_admin,
    )


@router.post(
    "/{worker_id}/activate",
    response_model=WorkerNodeResponse
)
def activate_worker(
    worker_id: str,
    db: db_session,
    current_user: current_active_user,
):
    """Activates a worker node, moving its status te 'active'."""
    is_admin = current_user.role == UserRole.admin
    return worker_service.activate_worker_node(
        db=db,
        worker_id=worker_id,
        user_id=current_user.id,
        is_admin=is_admin,
    )


@router.post(
    "/{worker_id}/deactivate",
    response_model=WorkerNodeResponse
)
def deactivate_worker(
    worker_id: str,
    db: db_session,
    current_user: current_active_user,
):
    """Deactivates a worker node, moving its status te 'deactiveted'."""
    is_admin = current_user.role == UserRole.admin
    return worker_service.deactivate_worker_node(
        db=db,
        worker_id=worker_id,
        user_id=current_user.id,
        is_admin=is_admin,
    )


@router.post(
    "/{worker_id}/remove",
    response_model=WorkerNodeResponse
)
def remove_worker(
    worker_id: str,
    payload: WorkerRemovalRequest,
    db: db_session,
    current_user: current_active_user,
):
    """Marks a node as 'removed' and stores the removal reason.
    Requires explanation for why removal."""
    is_admin = current_user.role == UserRole.admin
    return worker_service.remove_worker_node(
        db=db,
        worker_id=worker_id,
        reason=payload.reason,
        user_id=current_user.id,
        is_admin=is_admin,
    )


@router.get(
    "/compute-distribution",
    response_model=ComputeDistrubutionRatio,
    status_code=status.HTTP_200_OK,
)
def get_compute_distribution(db: Session = Depends(get_db)):
    operational_statuses = ["active", "busy", "quarantined", "offline"]

    counts = (
        db.query(WorkerNode.status, func.count(WorkerNode.id))
        .filter(WorkerNode.status.in_(operational_statuses))
        .group_by(WorkerNode.status)
        .all()
    )

    counts_dict = {status_key: count for status_key, count in counts}

    active_count = counts_dict.get("active", 0)
    busy_count = counts_dict.get("busy", 0)
    quarantined_count = counts_dict.get("quarantined", 0)
    offline_count = counts_dict.get("offline", 0)
    total_count = active_count + busy_count + quarantined_count + offline_count

    return ComputeDistrubutionRatio(
        active=active_count,
        busy=busy_count,
        quarantined=quarantined_count,
        offline=offline_count,
        total=total_count,
    )


@router.post("/keys", status_code=status.HTTP_201_CREATED, response_model=WorkerEnrollmentKeyResponse)
def generate_worker_enrollment_key(
    body: WorkerEnrollmentKeyRequest,
    current_user: current_active_user
):
    """Generates a single-use setup key for the authenticated user and caches it in Valkey."""
    return worker_service.generate_worker_key(current_user.id, label=body.label, gpu_name=body.gpu_name)


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
                    valkey.srem("worker:pool:busy", worker_id)
                    db.refresh(node)
                    if node.status == "busy":
                        node.status = "active"
                        db.commit()
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


async def dispatch_simulation_task(task_payload: dict, db: Optional[Session] = None) -> dict:
    if db is None:
        from app.backend.db import SessionLocal
        with SessionLocal() as session:
            return await dispatch_simulation_task(task_payload, db=session)
    
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
    if not node or node.status != "active":
        log.info("skipping worker %s, (status -> %s)", worker_id, node.status if node else "missing")
        valkey.srem("worker:pool:busy", worker_id)
        return {"dispatched_to": "cloud_fallback", "status": "queued"}

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

        log.warning("Worker %s exceeded %.0fs limit on job %s. Quarantining", worker_id, JOB_TIMEOUT_SECONDS, job_id)
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

