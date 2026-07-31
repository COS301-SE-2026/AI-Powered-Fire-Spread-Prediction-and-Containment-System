from datetime import datetime
from typing import List

from geoalchemy2.shape import to_shape
from pydantic import BaseModel, ConfigDict


class ContainmentLines(BaseModel):
    id: str
    fire_report_id: str
    line_geom: str
    drawn_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContainmentLinesList(BaseModel):
    data: List[ContainmentLines]
    total: int


class CreateContainmentLine(BaseModel):
    wkt: str
