# for volunteer GPU workers

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from db import Base
from models.users import User


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
    driver_version = Column(String(50), nullable=True)

    # state include: active, busy offline, rejected, quarentined, deactivated, removed
    status = Column(String(20), nullable=True)

    # reliability
    consecutive_failures = Column(Integer, default=0, nullable=False)
    quarentine_until = Column(DateTime(timezone=True), nullable=True)
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)

    # timestamps for state transitions for UI
    activated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deactivated_at = Column(DateTime(timezone=True), nullable=True)
    removed_at = Column(DateTime(timezone=True), nullable=True)
    removal_reason = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship(User, foreign_keys=[user_id], backref="worker_nodes")


