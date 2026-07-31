from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

from enums.fire_danger import FireDanger
from enums.report_status import ReportStatus


class NearbyFire(BaseModel):
    location_text: str
    distance: float
    time_ago: str
    status: ReportStatus

    model_config = ConfigDict(from_attributes=True)


class EnvironmentVariables(BaseModel):
    wind: float
    wind_dir: int  # wind angle in degrees
    temperature: float
    fire_danger: FireDanger
    humidity: float


class NearbyFiresList(BaseModel):
    data: List[NearbyFire]
    total: int


class DashboardData(BaseModel):
    nearby_fires: NearbyFiresList
    environment_variables: EnvironmentVariables
