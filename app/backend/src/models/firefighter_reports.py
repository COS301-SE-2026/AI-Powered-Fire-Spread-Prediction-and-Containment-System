from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enums.firefighter_status import FirefighterReportStatus
from geoalchemy2 import Geometry
from db import Base

class Firefighter_FireReports(Base):
    __tablename__ = "firefighter_fire_reports"

    id = Column(String, primary_key=True)
    reference_number = Column(String(20), unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True) 
    reporter_ip = Column(String, nullable=True)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=False)
    location_text = Column(Text, nullable=False)
    location_geom = Column(Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=False)
    boundary_radius = Column(Numeric(5,2), nullable=True)
    status = Column(Enum(FirefighterReportStatus), default=FirefighterReportStatus.pending, nullable=False)
    status_index = Column(Integer, default=0, nullable=False)
    reported = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc).date())
    user = relationship("User", back_populates='firefighter_fire_reports')