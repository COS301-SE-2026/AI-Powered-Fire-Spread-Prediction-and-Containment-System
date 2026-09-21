from datetime import datetime, timezone

from geoalchemy2 import Geometry
from sqlalchemy import Column, Date, DateTime, Enum, Float, ForeignKey, String, Text

from app.backend.db import Base
from app.backend.src.enums.resource import CapacityUnit, ResourceStatus, ResourceType

class WaterResource(Base):
    """A resource (tank, dam, crew, ...) a person has offered for use in a fire emergency"""
    
    __tablename__ = "water_resources"
    __table_args__ = {"extend_existing": True}
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True)
    
    resource_type = Column(Enum(ResourceType), nullable=False, index=True)
    other_resource = Column(String(100), nullable=True) # only set when type == other
    
    capacity = Column(Float, nullable=False)
    capacity_unit = Column(Enum(CapacityUnit), nullable=False)
    other_capacity_unit = Column(String(50), nullable=True) # only set when type == other
    
    status = Column(Enum(ResourceStatus), default=ResourceStatus.available, nullable=False)
    
    # The from only captures dates so these dates (not timestamps) to avoid timezone.shifts.
    # available_until is inclusive; NULL means indefininely.
    available_from = Column(Date, nullable=False)
    available_until = Column(Date, nullable=True)
    
    location_text = Column(Text, nullable=False)
    location_geom = Column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=False
    )
    
    name = Column(String(100), nullable=False)
    contact = Column(String(30), nullable=False)
    
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.uct),
        nullable=False,
    )
