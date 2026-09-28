from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class SavedLocationCreate(BaseModel):
    label: str = Field(min_length=1, max_length=50)
    address: str = Field(min_length=1, max_length=225)
    lat: float | None = Field(deafult=None, ge=-90, le=90)
    lng: float | None = Field(deafult=None, ge=-180, le=180)

class SavedLocationUpdate(BaseModel):
    label: str = Field(deafult=None, min_length=1, max_length=50)
    address: str = Field(deafult=None, min_length=1, max_length=225)
    lat: float | None = Field(deafult=None, ge=-90, le=90)
    lng: float | None = Field(deafult=None, ge=-180, le=180)

class SavedLocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    label: str
    address: str
    lat: float | None
    lng: float | None
    created_at: datetime