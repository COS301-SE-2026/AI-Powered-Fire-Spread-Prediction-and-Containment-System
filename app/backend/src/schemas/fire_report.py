from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enums.report_status import ReportStatus

class FireReportCreate(BaseModel):
    lat: float
    lng: float
    location_text:str
    description:Optional[str] = None
    image_url:str
    boundary_radius: float

class FireReportMapResponse(BaseModel):
    id:str
    reference_number:str
    lat: float
    lng: float
    location_text:str
    status:ReportStatus
    boundary_radius: float
    size: float
    submitted_at:datetime
    reporter_name: Optional[str] = None

    class Config:
        from_attributes = True

class FireReportDetailResponse(BaseModel):
    id:str
    reference_number:str
    lat: float
    lng: float
    location_text:str
    description:Optional[str] = None
    image_url: str
    status:ReportStatus
    boundary_radius: float
    size: float
    submitted_at: datetime
    reporter_name: Optional[str] = None

    class Config:
        from_attributes = True