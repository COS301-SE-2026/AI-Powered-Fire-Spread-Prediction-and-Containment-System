# for disributed system for volunteer gpus
import os
import secrets
import shlex
from typing import Optional, List

from fastapi import HTTPException, status
import redis
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.backend.src.dependencies.auth import create_access_token
from app.backend.src.models.workers import WorkerNode
from app.backend.src.schemas.workers import WorkerRegisterRequest
from app.backend.src.enums.worker_status import WorkerStatus

VALKEY_HOST = os.getenv("VALKEY_HOST", "localhost")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", 6379))

# connection to Valkey cache
valkey_client = redis.Redis(
    host=VALKEY_HOST,
    port=VALKEY_PORT,
    db=0,
    decode_responses=True,
)

REGISTRATION_KEY_TTL = 86400 # 24 hours
MIN_VRAM_MB = 4096


def list_workers(
    db: Session,
    user_id: Optional[str] = None,
    is_admin: bool = False,
) -> List[WorkerNode]:
    """Returns all workers for admins, or scopes the list to user_id for volunteers."""
    query = db.query(WorkerNode)
    if not is_admin:
        query = query.filter(WorkerNode.user_id == user_id)
    return query.order_by(WorkerNode.activated_at.desc()).all()


def activate_worker_node(
    db: Session,
    worker_id: str,
    user_id: str,
    is_admin: bool = False,
) -> WorkerNode:
    node = db.query(WorkerNode).filter(WorkerNode.id == worker_id).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker node not found",
        )

    if not is_admin and node.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Not authorized to activate this worker node",
        )

    if node.status != WorkerStatus.deactivated:
        return node # already active

    node.status = "active"
    node.activated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(node)
    valkey_client.sadd("worker:pool:idle", worker_id)
    return node


def deactivate_worker_node(
    db: Session,
    worker_id: str,
    user_id: str,
    is_admin: bool = False,
) -> WorkerNode:
    node = db.query(WorkerNode).filter(WorkerNode.id == worker_id).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker node not found",
        )

    if not is_admin and node.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Not authorized to deactivate this worker node",
        )

    if node.status == WorkerStatus.removed and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This worker was removed by an administrator"
            )

    node.status = "deactivated"
    node.deactivated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(node)
    valkey_client.srem("worker:pool:idle", worker_id)
    return node


def remove_worker_node(
    db: Session,
    worker_id: str,
    reason: Optional[str],
    user_id: str,
    is_admin: bool = False,
) -> WorkerNode:
    node = db.query(WorkerNode).filter(WorkerNode.id == worker_id).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker node not found",
        )

    if not is_admin and node.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail = "Not authorized to remove this worker node",
        )

    if is_admin and (not reason or not reason.strip()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reason for removal is required for GPU removal",
        )

    node.status = "removed"
    node.removed_at = datetime.now(timezone.utc)
    node.removal_reason = reason.strip() if reason else None
    db.commit()
    db.refresh(node)
    valkey_client.srem("worker:pool:idle", worker_id)
    return node


def generate_worker_key(
        user_id: str,
        label: str = "volunteer-desktop",
        gpu_name: str = "Unkown GPU",
) -> dict:
    """Generates single-use setup key and stores in Valkey with 24 h TTL to authenticate user"""

    token_suffix = secrets.token_hex(8).upper()
    reg_key = f"REG-{token_suffix}"

    valkey_storage_key = f"worker:reg:{reg_key}"

    # SETEX worker:reg:<key> 86400 <user_id>
    valkey_client.setex(valkey_storage_key, REGISTRATION_KEY_TTL, user_id)

    backend_url = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8000")
    ws_url = backend_url.rstrip("/").replace("http", "ws", 1) + "/api/v1/workers/connect"

    return {
        "registration_key": reg_key,
        "expires_in_seconds": REGISTRATION_KEY_TTL,
        "docker_command": (
            f'docker run --gpus all --memory="8g" '
            f'-e REGISTRATION_KEY={shlex.quote(reg_key)} '
            f'-e WORKER_LABEL={shlex.quote(label)} '
            f'-e BACKEND_BASE_URL={shlex.quote(backend_url)} '
            f'-e WEBSOCKET_URL={shlex.quote(ws_url)} '
            f'fireaway-worker:latest'
        ),
    }

issue_enrollment_key = generate_worker_key


def register_worker_node(db: Session, register_data: WorkerRegisterRequest) -> dict:
    """Atomically retrieves and burns the single-use key from Valkey,
    validates the hardware capacity,
    registers the node in PostgreSQL,
    and returns a scoped Worker Device JWT."""

    valkey_storage_key = f"worker:reg:{register_data.registration_key}"

    # atomic claim and burn prevents duplicate registration
    pipe = valkey_client.pipeline()
    pipe.get(valkey_storage_key)
    pipe.delete(valkey_storage_key)
    results = pipe.execute()
    user_id = results[0]

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired worker registration key",
        )

    # hardware capacity
    if register_data.vram_mb < MIN_VRAM_MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Worker rejected. Insufficient VRAM. "
                f"Detected {register_data.vram_mb} MB, min VRAM required is {MIN_VRAM_MB} MB"
            ),
        )

    # new active
    node = WorkerNode(
        user_id=user_id,
        label=getattr(register_data, "label", "volunteer-desktop"),
        gpu_name=register_data.gpu_name,
        vram_mb=register_data.vram_mb,
        driver_version=register_data.driver_version,
        status="active",
        consecutive_failures=0,
    )
    db.add(node)
    db.commit()
    db.refresh(node)

    device_token = create_access_token(
        data={
            "sub": node.id,
            "user_id": user_id,
            "role": "worker_node",
            "type": "worker_device",
        }
    )

    return {
        "access_token": device_token,
        "token_type": "bearer",
        "worker_id": node.id,
    }