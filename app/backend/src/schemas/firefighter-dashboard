from enums.report_status import ReportStatus
from enums.fire_danger import FireDanger
from typing import List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class NearbyFire(BaseModel):
    location_text: str
    distance: float
    time_ago: str
    status: ReportStatus

class EnvironmentVariables(BaseModel):
    wind: float
    wind_dir: int # wind angle in degrees 
    temperature: float
    fire_danger: FireDanger
    humidity: float

class NearbyFiresList(BaseModel):
    data: List[NearbyFire]
    total: int