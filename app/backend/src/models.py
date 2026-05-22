import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, Enum, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from pydantic import BaseModel
from typing import Optional, Literal
from db import Base

class ReportStatus(str, enum.Enum):
    received = "received"
    pending = "pending"
    verified = "verified"
    notified = "notified"

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
    fire_reports = relationship("FireReportModel", back_populates="user")

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

class FireReportModel(Base):
    __tablename__ = "fire_reports"

    id: Mapped[str] = mapped_column(String, primary_key=True, server_default=func.gen_random_uuid())
    reference_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    
    user_id: Mapped[str | None] = mapped_column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    location_text: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", server_default="")
    location_geom = mapped_column(Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=False)
    boundary_radius_km: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus), default=ReportStatus.received, nullable=False)
    status_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="fire_reports")

StatusType = Literal["received", "pending", "verified", "notified"]

class FireReportCreate(BaseModel):
    location: str
    description: Optional[str] = ""
    lat: float
    lng: float
    boundary_radius_km: Optional[float] = None
    user_id: Optional[str] = None 

class FireReport(BaseModel):
    reference_number: str
    user_id: Optional[str] = None 
    location: str
    description: str
    lat: float
    lng: float
    boundary_radius_km: Optional[float] = None
    status: StatusType
    status_index: int
    submitted_at: str

    class Config:
        from_attributes = True