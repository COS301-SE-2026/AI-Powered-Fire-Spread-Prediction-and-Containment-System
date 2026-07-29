from pydantic import BaseModel
from typing import List


class ActivityItemSchema(BaseModel):
    id: str
    message: str
    timeAgo: str


class WeeklyDataSchema(BaseModel):
    day: str
    count: int


class TopMetricsSchema(BaseModel):
    active_fires: int
    pending_approvals: int
    total_users: int
    system_status: str


class SystemMetricsSchema(BaseModel):
    predictions_completed: int
    model_health: str
    avg_confidence_percent: int
    last_sync_time: str


class DashboardSummaryResponse(BaseModel):
    top_metrics: TopMetricsSchema
    activity_log: List[ActivityItemSchema]
    weekly_incidents: List[WeeklyDataSchema]
    system_metrics: SystemMetricsSchema
