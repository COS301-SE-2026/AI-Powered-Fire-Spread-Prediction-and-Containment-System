from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from src.enums.user_role import UserRole
from datetime import datetime, timezone
from src.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    id_number = Column(String(13), nullable=False, unique=True)
    license_number = Column(String)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    fire_reports = relationship("FireReports", back_populates="user")
    role_requests = relationship("RoleRequest", back_populates="user", foreign_keys="RoleRequest.user_id")
    


