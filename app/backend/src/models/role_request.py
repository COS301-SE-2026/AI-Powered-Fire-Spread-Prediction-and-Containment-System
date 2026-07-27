from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from enums.role_request_status import RequestStatus
from enums.user_role import UserRole
from db import Base

class RoleRequest(Base):
    __tablename__ = "role_requests"

    request_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    requested_role = Column(Enum(UserRole), default=UserRole.ADMIN, nullable=False)
    current_role = Column(Enum(UserRole), nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING, nullable=False)
    firefighter_license_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    reviewed_by = Column(String, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    user = relationship("User", foreign_keys=[user_id], back_populates="role_requests")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
