from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from enums.report_status import ReportStatus

from typing import List, Optional


# response structure for the reported fires table
class FirefighterReportTable(BaseModel):
    ref: str = Field(validation_alias="reference_number")
    location: str = Field(validation_alias="location_text")
    status: ReportStatus
    size: float = Field(validation_alias="boundary_radius")
    reported: datetime = Field(validation_alias="submitted_at")
    reporter: str
    verification_notes: Optional[str] = None
    lat: float
    lng: float

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FirefighterReportModal(BaseModel):
    id: str
    ref: str = Field(validation_alias="reference_number")
    location: str = Field(validation_alias="location_text")
    status: ReportStatus
    reported: datetime = Field(validation_alias="submitted_at")
    reporter: str
    description: str
    image_url: str
    size: float = Field(validation_alias="boundary_radius")
    verification_notes: Optional[str] = None
    lat: float
    lng: float

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ReportList(BaseModel):
    data: List[FirefighterReportTable]
    total: int
