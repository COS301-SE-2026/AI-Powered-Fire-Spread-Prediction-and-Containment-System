from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from db import get_db
from enums.report_status import ReportStatus
from enums.role_request_status import RequestStatus

# from auth import get_current_admin_user



router = APIRouter(
    prefix="/api/admin/dashboard",
    tags=["Admin Dashboard"],
    # comment when need admin auth
    # dependencies=[Depends(get_current_admin_user)]
)


def _as_aware(dt):
    """Normalise datetime"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)




def _time_ago(dt) -> str:
    dt = _as_aware(dt)
    if dt is None:
        return "unknown"
    delta = datetime.now(timezone.utc) - dt
    minutes = int(delta.total_seconds() // 60)
    if minutes < 1:
        return "just now"
    if minutes < 60:
        return f"{minutes} min ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hr ago"
    return f"{hours // 24} day(s) ago"



@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)) -> Any:
    """Retrieves all aggregate data required to render admin dashboard"""

    # need to add a state for fires that is not active anymore
    # need to add a state for fires that is not active anymore
    active_fires = db.query(func.count(FireReports.id)).scalar()

    pending_approvals = (
        db.query(func.count(RoleRequest.request_id))
        .filter(RoleRequest.status == RequestStatus.pending)
        .scalar()
    )

    total_users = db.query(func.count(User.id)).scalar()

    # need actual health check (does not exist yet)
    # need actual health check (does not exist yet)
    system_status = "ALERT" if active_fires > 10 else "OKAY"

    # will pull the metrics from db at some point
    # will pull the metrics from db at some point
    top_metrics = {
        "active_fires": active_fires,
        "pending_approvals": pending_approvals,
        "total_users": total_users,
        "system_status": system_status,
    }

    recent_fires = (
        db.query(FireReports).order_by(FireReports.submitted_at.desc()).limit(5).all()
        db.query(FireReports).order_by(FireReports.submitted_at.desc()).limit(5).all()
    )
    recent_role_requests = (
        db.query(RoleRequest)
        .filter(RoleRequest.reviewed_at.isnot(None))
        .order_by(RoleRequest.reviewed_at.desc())
        .limit(5)
        .all()
    )

    activity_items = []
    for report in recent_fires:
        activity_items.append(
            {
                "id": f"fire-{report.id}",
                "message": f"New fire reported - {report.location_text}",
                "timeAgo": _time_ago(report.submitted_at),
                "_sort_ts": _as_aware(report.submitted_at),
            }
        )
        activity_items.append(
            {
                "id": f"fire-{report.id}",
                "message": f"New fire reported - {report.location_text}",
                "timeAgo": _time_ago(report.submitted_at),
                "_sort_ts": _as_aware(report.submitted_at),
            }
        )
    for rr in recent_role_requests:
        activity_items.append(
            {
                "id": f"role-{rr.request_id}",
                "message": f"Role {rr.status.value} - {rr.user_id} ({rr.requested_role.value})",
                "timeAgo": _time_ago(rr.reviewed_at),
                "_sort_ts": _as_aware(rr.reviewed_at),
            }
        )
        activity_items.append(
            {
                "id": f"role-{rr.request_id}",
                "message": f"Role {rr.status.value} - {rr.user_id} ({rr.requested_role.value})",
                "timeAgo": _time_ago(rr.reviewed_at),
                "_sort_ts": _as_aware(rr.reviewed_at),
            }
        )

    activity_log = sorted(
        activity_items,
        key=lambda x: x["_sort_ts"] or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )[:7]
    for item in activity_log:
        item.pop("_sort_ts", None)

    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_week_fires = (
        db.query(FireReports).filter(FireReports.submitted_at >= seven_days_ago).all()
        db.query(FireReports).filter(FireReports.submitted_at >= seven_days_ago).all()
    )

    day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    counts_by_day = {day: 0 for day in day_order}
    for report in recent_week_fires:
        day_name = report.submitted_at.strftime("%a")
        if day_name in counts_by_day:
            counts_by_day[day_name] += 1

    weekly_incidents = [{"day": day, "count": counts_by_day[day]} for day in day_order]

    system_metrics = {
        "predictions_completed": 0,
        "model_health": "Unknown",
        "avg_confidence_percent": 0,
        "last_sync_time": "Not yet tracked",
        "last_sync_time": "Not yet tracked",
    }

    return {
        "top_metrics": top_metrics,
        "activity_log": activity_log,
        "weekly_incidents": weekly_incidents,
        "system_metrics": system_metrics,
        "system_metrics": system_metrics,
    }

