from typing import List

from pydantic import BaseModel

from app.backend.src.schemas.role_request import RoleRequestResponse


class KPIs(BaseModel):
    total_users: int
    pending_role_requests: int
    total_firefighters: int
    total_admins: int


class AnalyticsOverviewResponse(BaseModel):
    kpis: KPIs
    pending_requests: List[RoleRequestResponse]
