from datetime import datetime, timezone

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.backend.db import Base
from app.backend.src.enums.user_role import UserRole


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
    #pasword reset 
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    location_geom = Column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=True
    )

    fire_reports = relationship("FireReports", back_populates="user")
    role_requests = relationship("models.role_request.RoleRequest",
                                 foreign_keys="[RoleRequest.user_id]",
                                back_populates="user")