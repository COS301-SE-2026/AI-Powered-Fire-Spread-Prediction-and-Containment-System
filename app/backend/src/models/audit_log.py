from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Text
from enums.audit_action import AuditAction
from db import Base

class AuditLog(Base):
    __tablename__="audit_log"

    id=Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"),nullable=False)
    action=Column(Enum(AuditAction),nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
