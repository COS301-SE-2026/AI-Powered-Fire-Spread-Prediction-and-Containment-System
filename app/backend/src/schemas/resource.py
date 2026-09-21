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
    
    @field_validator("available_from", "available_until", "fire_ref", mode="before")
    @classmethod
    def blank_to_none(cls, v):
        # form sends '' for "no end date" / "no fire"
        if isinstance(v, str) and v.strip() == "":
            return None
        return v
    
    @field_validator("name", "location", "other_resource", "other_capacity", "contact")
    @classmethod
    def strip_text(cls, v: str) -> str:
        return v.strip()
    
    @field_validator("location")
    @classmethod
    def location_not_blank(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Location must be at least 3 characters long")
        return v
    
    @field_validator("name")
    @classmethod
    def name_valid(cls, v: str) -> str:
        if v == "":
            raise ValueError("Enter a name for this resource.")
        if v.isdigit():
            raise ValueError("Name cannot be only numbers.")
        if len(v) < 3:
            raise ValueError("Name must be at least 3 characters long.")
        return v
    
    @field_validator("contact")
    @classmethod
    def contact_valid(cls, v: str) -> str:
        digits = re.sub(r"\D", "", v)
        is_local = len(digits) == 10 and digits.startswith("0")
        is_intl = len(digits) == 11 and digits.startswith("27")
        if not (is_local or is_intl):
            raise ValueError("Enter a valid 10-digit phone number.")
        if re.fullmatch(r"(\d)\1+", digits):
            raise ValueError("This phone number is invalid")
        return v
    
    @field_validator("external_pin")
    @classmethod
    def pin_not_null_island(cls, v: Pin) -> Pin:
        if v.lat == 0 and v.lng == 0:
            raise ValueError("Pin a location on the map or search for an address.")
        return v
    
    @model_validator(mode="after")        
    def cross_field_checks(self):
        if self.capacity != self.capacity or self.capacity <= 0:    # Nan or non-positive
            raise ValueError("Capacity must be a positive number.")
        
        if self.resource == ResourceType.crew:
            if self.capacity > MAX_CREW:
                raise ValueError(f"Crew size cannot exceed {MAX_CREW}.")
            if not float(self.capacity).is_integer():
                raise ValueError("Crew size must be a whole number.")
        elif self.capacity > MAX_CAPACITY:
            raise ValueError(f"Capacity cannot exceed {MAX_CAPACITY:,}.")
        
        if self.resource == ResourceType.other:
            if self.other_resource == "":
                raise ValueError("Tell us what type of resource this is.")
        else:
            self.other_resource = ""
            self.other_capacity = ""
            
        if self.available_from is None:
            self.available_from = datetime.now(timezone.utc).data()
        if self.available_until is not None and self.available_until < self.available_from:
            raise ValueError("'Available until' cannot be before 'available from'.")
        return self
    
class ResourceResponse(CamelModel):
    id: str
    resource: ResourceType
    other_resource: str
    capacity: float
    capacity_unit: CapacityUnit
    other_capacity: str
    status: ResourceStatus
    available_from: date
    available_until: Optional[date] = None
    location: str
    external_pin: Pin
    name: str
    contact: str
    
class ResourceListResponse:
    data: List[ResourceResponse]
    total: int
    