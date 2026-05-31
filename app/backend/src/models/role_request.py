from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from src.enums.role_request_status import RequestStatus
from src.enums.user_role import UserRole
from datetime import datetime, timezone
from src.db import Base

class RoleRequest(Base):
    __tablename__ = "role_requests"

    request_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    requested_role = Column(Enum(UserRole), default=UserRole.admin, nullable=False)
    current_role = Column(Enum(UserRole), nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.pending, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    reviewed_by = Column(String, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    user = relationship("User", foreign_keys=[user_id], back_populates="role_requests")
    reviewer = relationship("User", foreign_keys=[reviewed_by])