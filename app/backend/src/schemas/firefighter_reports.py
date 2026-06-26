from enums.firefighter_status import FirefighterReportStatus
from typing import List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# response structure for the reported fires table
class FirefighterReportTable(BaseModel):
    ref: str = Field(validation_alias="reference_number")
    location: str = Field(validation_alias="location_text")
    status: FirefighterReportStatus
    size: float = Field(validation_alias="boundary_radius")
    reported: datetime
    reporter: str

    model_config = ConfigDict(from_attributes = True, populate_by_name=True)

class FirefighterReportModal(BaseModel):
    ref: str = Field(validation_alias="reference_number")
    location: str = Field(validation_alias="location_text")
    status: FirefighterReportStatus
    reported: datetime
    description: str
    image_url: str
    size: float = Field(validation_alias="boundary_radius")

    
    model_config = ConfigDict(from_attributes = True, populate_by_name=True)

class ReportList(BaseModel):
    data: List[FirefighterReportTable]
    total: int