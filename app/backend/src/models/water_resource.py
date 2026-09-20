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