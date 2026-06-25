from enums.firefighter_status import FirefighterReportStatus
from typing import List
from datetime import datetime
from pydantic import BaseModel

# response structure for the reported fires table
class FirefighterReportTable(BaseModel):
    ref: str
    location: str
    status: FirefighterReportStatus
    size: float
    reported: datetime
    reporter: str

    class Config:
        from_attributes = True

class FirefighterReportModal(BaseModel):
    ref: str
    location: str
    status: FirefighterReportStatus
    reported: datetime
    description: str
    img_url: str
    size: float

    class Config:
        from_attributes = True

class ReportList(BaseModel):
    data: List[BaseModel]
    total: int