import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    name = Column(String)
    surname = Column(String)
    id_number = Column(String)
    license_number = Column(String)
    role = Column(String, default="User")
    totp_secret = Column(String)
    is_2fa_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RoleRequestDB(Base):
    __tablename__ = "role_requests"
    
    request_id = Column(String, primary_key=True, default=lambda: f"req_{uuid.uuid4().hex[:8]}")
    user_id = Column(String, nullable=False)
    user_full_name = Column(String)
    email = Column(String)
    role = Column(String, nullable=False)
    status = Column(String, default="pending", nullable=False)
    firefighter_license_id = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))