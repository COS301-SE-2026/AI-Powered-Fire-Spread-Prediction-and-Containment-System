from datetime import datetime, timezone

from db import Base
from enums.user_role import UserRole
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    id_number = Column(String(13), nullable=False, unique=True)
    license_number = Column(String)
    hashed_password = Column(String, nullable=False, default="")
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    is_active = Column(Boolean, default=True)
    is_2fa_enabled = Column(Boolean, default=False)
    totp_secret = Column(String, nullable=True)

    fire_reports = relationship("FireReports", back_populates="user")
    role_requests = relationship(
        "RoleRequest", back_populates="user", foreign_keys="RoleRequest.user_id"
    )
