from datetime import datetime, timezone
from app.backend.src.models.users import User

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.backend.db import Base
from app.backend.src.enums.role_request_status import RequestStatus
from app.backend.src.enums.user_role import UserRole


class RoleRequest(Base):
    __tablename__ = "role_requests"
    __table_args__ = {"extend_existing": True}

    request_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    requested_role = Column(Enum(UserRole), default=UserRole.admin, nullable=False)
    current_role = Column(Enum(UserRole), nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.pending, nullable=False)
    firefighter_license_id = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    reviewed_by = Column(String, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    user = relationship(User, foreign_keys=[user_id], back_populates="role_requests")
    reviewer = relationship(User, foreign_keys=[reviewed_by])
