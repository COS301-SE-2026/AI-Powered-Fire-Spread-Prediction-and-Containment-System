from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from enums.report_status import ReportStatus
from enums.report_priority import ReportPriority


class FireReportCreate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    location_text: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    image_url: Optional[str] = None
    boundary_radius: float = Field(..., gt=0, le=50)
    photo_hash: Optional[str] = None


class FireReportMapResponse(BaseModel):
    id: str
    reference_number: str
    lat: float
    lng: float
    location_text: str
    status: ReportStatus
    boundary_radius: float
    size: float
    submitted_at: datetime
    reporter_name: Optional[str] = None
    verification_notes: Optional[str] = None

    class Config:
        from_attributes = True


class FireReportDetailResponse(BaseModel):
    id: str
    reference_number: str
    lat: float
    lng: float
    location_text: str
    description: Optional[str] = None
    image_url: str
    status: ReportStatus
    boundary_radius: float
    size: float
    submitted_at: datetime
    reporter_name: Optional[str] = None

    # for auto fire report verification
    priority: ReportPriority
    system_verified: bool
    verification_notes: Optional[str] = None

    class Config:
        from_attributes = True
