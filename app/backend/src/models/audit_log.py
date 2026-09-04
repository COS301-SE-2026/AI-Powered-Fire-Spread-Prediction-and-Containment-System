from datetime import datetime, timezone

from geoalchemy2 import Geometry
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.backend.db import Base
from app.backend.src.enums.audit_action import AuditAction


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    action = Column(Enum(AuditAction), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
