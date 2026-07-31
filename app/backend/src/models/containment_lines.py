from datetime import datetime, timezone

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from db import Base


# stores all the lines that are drawn and stores them based on proximity to an existing fire
class ContainmentLines(Base):
    __tablename__ = "containment_lines"

    id = Column(String, primary_key=True)
    fire_report_id = Column(
        String, ForeignKey("fire_reports.id", ondelete="CASCADE"), nullable=False
    )
    line_geom = Column(
        Geometry(geometry_type="LINESTRING", srid=4326, spatial_index=True),
        nullable=False,
    )
    drawn_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    fire_report = relationship("FireReports", back_populates="containment_lines")
