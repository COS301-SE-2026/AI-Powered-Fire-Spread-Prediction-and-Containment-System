import re 
from datetime import date, datetime, timezone
from typing import List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from pydantic.alias_generators import to_camel

from app.backend.src.enums.resource import CapacityUnit, ResourceStatus, ResourceType

MAX_CAPACITY = 150_000
MAX_CREW = 1_000

class CamelModel(BaseModel):
    """The frontend speaks camelCase"""
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )
    
class Pin(CamelModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    
class ResourceCreate(CamelModel):
    resource: ResourceType
    other_resource: str = Field(default="", max_length=100)
    other_capacity: str = Field(default="", max_length=50)
    capacity: float
    # sent from frontend but derived server-side from `resource`; accept & ignored
    capacity_unit: Optional[CapacityUnit] = None
    available_from: Optional[date] = None
    available_until: Optional[date] = None
    location: str = Field(..., max_length=255)
    external_pin: Pin
    name: str = Field(..., max_length=100)
    contact: str = Field(..., max_length=30)
    fire_ref: Optional[str] = Field(default=None, max_length=20)
    
    @field_validator("availab;e_from", "available_until", "fire_ref", mode="before")
    @classmethod
    def blank_to_none(cls, v):
        # form sends '' for "no end date" / "no fire"
        if isinstance(v, str) and v.strip() == "":
            return None
        return v
    
    