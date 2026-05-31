from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from geoalchemy2 import Geometry
from src.db import Base

class FireReports(Base):
    __tablename__ = "fire_reports"

    id = Column(String, primary_key=True)
    reference_number = Column(String(20), unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reporter_ip = Column(String, nullable=True)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=False)
    location_text = Column(Text, nullable=False)
    location_geom = Column(Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=False)
    boundary_radius = Column(Numeric(5,2), nullable=True)
    status = Column(Enum(ReportStatus), default=ReportStatus.received, nullable=False)
    status_index = Column(Integer, default=0, nullable=False)
    submitted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    user = relationship("User", back_populates='fire_reports')