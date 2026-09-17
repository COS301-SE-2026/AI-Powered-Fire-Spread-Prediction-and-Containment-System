# for volunteer GPU workers

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db import Base
from models.users import User
from app.backend.src.enums.worker_status import WorkerStatus

def generate_uuid() -> str:
    return str(uuid.uuid4())

class WorkerNodeRequest(Base):
    __tablename__ = "worker_node_request"
    __tablen_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    label = Column(String(100), nullable=False)
    gpu_name = Column(String(100), nullable=False)
    vram_mb = Column(Integer, nullable=False)
    status = Column(String(20), default=WorkerStatus.pending, nullable=)
