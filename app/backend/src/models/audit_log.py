from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Enum,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enums.audit_action import AuditAction
from geoalchemy2 import Geometry
from db import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    action = Column(Enum(AuditAction), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
