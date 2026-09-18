# for disributed system for volunteer gpus
import os
import secrets
from typing import Optional

from fastapi import HTTPException, status
import redis
from sqlalchemy.orm import Session

from dependencies.auth import create_access_token
from models.workers import WorkerNode
from schemas.workers import WorkerRegisterRequest

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


def generate_worker_key(user_id: str) -> dict:
    """Generates single-use setup key and stores in Valkey with 24 h TTL to authenticate user"""

    token_suffix = secrets.token_hex(8).upper()
    reg_key = f"REG-{token_suffix}"

    valkey_storage_key = f"worker:reg:{reg_key}"

    # SETEX worker:reg:<key> 86400 <user_id>
    valkey_client.setex(valkey_storage_key, REGISTRATION_KEY_TTL, user_id)

    return {
        "registration_key": reg_key,
        "expires_in_seconds": REGISTRATION_KEY_TTL,
        "docker_command": (
            f'docker rin --gpus all -e REGISTRATION_KEY="{reg_key}" '
            f'fireaway-worker:latest'
        ),
    }


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
