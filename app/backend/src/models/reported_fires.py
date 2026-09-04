from datetime import datetime, timezone
from app.backend.src.models.users import User

from geoalchemy2 import Geometry
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.backend.db import Base
from app.backend.src.enums.report_status import ReportStatus

from sqlalchemy import Boolean
from app.backend.src.enums.report_priority import ReportPriority


class FireReports(Base):
    __tablename__ = "fire_reports"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True)
    reference_number = Column(String(20), unique=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reporter_ip = Column(String, nullable=True)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    location_text = Column(Text, nullable=False)
    location_geom = Column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=False
    )
    boundary_radius = Column(Numeric(5, 2), nullable=False)
    status = Column(Enum(ReportStatus), default=ReportStatus.received, nullable=False)
    status_index = Column(Integer, default=0, nullable=False)
    submitted_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship(User, back_populates="fire_reports")
    containment_lines = relationship("ContainmentLines", back_populates="fire_report")

    # for the autoverification of fire reports
    priority = Column(
        Enum(ReportPriority), default=ReportPriority.normal, nullable=False
    )
    system_verified = Column(Boolean, default=False, nullable=False)
    verification_notes = Column(Text, nullable=True)

    # for verification of the photo hash
    photo_hash = Column(String(64), nullable=True, index=True)

    @property
    def reporter(self) -> str:
        if self.user is None:
            return "Anonymous"
        return f"{self.user.name} {self.user.surname}"