from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from src.schemas.admin_dashboard import DashboardSummaryResponse
from src.db import get_db
from src.auth import get_current_admin_user

router = APIRouter(
    prefix="/api/admin/dashboard",
    tags=["Admin Dashboard"],
    dependencies=[Depends(get_current_admin_user)]
)

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)) -> Any:
    """Retrieves all aggregate data required to render admin dashboard"""

    #will pull the metrics from db at some point
    top_metrics = {
        "active_fires": 12,
        "pending_approvals": 5,
        "total_users": 284,
        "system_status": "OKAY"
    }

    activity_log = [
        {"id": 'log-1', "message": 'New fire reported - Pretoria West', "timeAgo": '2 min ago'},
        {"id": 'log-2', "message": 'New fire reported - Pretoria West', "timeAgo": '34 min ago'},
        {"id": 'log-3', "message": 'Fire contained - Centurion', "timeAgo": '52 min ago'},
        {"id": 'log-4', "message": 'Role request submitted - T.Mokiena (Firefighter)', "timeAgo": '1 hr ago'},
        {"id": 'log-5', "message": 'Role approved - A.Dlamini (Analyst)', "timeAgo": '2 hr ago'},
        {"id": 'log-6', "message": 'AI spread simulation completed - Mamelodi', "timeAgo": '2 hr ago'},
        {"id": 'log-7', "message": 'Containment line logged - Hatfield', "timeAgo": '3 hr ago'},
    ]

    weekly_incidents = [
        {"day": 'Mon', "count": 4},
        {"day": 'Tue', "count": 7},
        {"day": 'Wed', "count": 12},
        {"day": 'Thu', "count": 9},
        {"day": 'Fri', "count": 15},
        {"day": 'Sat', "count": 6},
        {"day": 'Sun', "count": 3},
    ]

    system_metrics = {
        "predictions_completed": 142,
        "model_health": "Operational",
        "avg_confidence_percent": 87,
        "last_sync_time": "Updated 3 min ago"
    }

    return {
        "top_metrics": top_metrics,
        "activity_log": activity_log,
        "weekly_incidents": weekly_incidents,
        "system_metrics": system_metrics
    }