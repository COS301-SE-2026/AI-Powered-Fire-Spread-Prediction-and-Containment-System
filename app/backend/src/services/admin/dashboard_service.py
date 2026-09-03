from datetime import datetime, timezone, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from enums.report_status import ReportStatus
from enums.role_request_status import RequestStatus
from models.reported_fires import FireReports
from models.users import User
from models.role_request import RoleRequest


def as_aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def calculate_time_ago(
    reported_at: datetime,
) -> str:  # return a string for how long ago fire has been reported
    reported_at = as_aware(reported_at)
    now = datetime.now(timezone.utc)
    difference = now - reported_at
    minutes = int(difference.total_seconds() // 60)

    if minutes < 1:
        return "just now"
    if minutes < 60:
        return f"{minutes} min ago"

    hours = minutes // 60

    if hours == 1:
        return f"1 hr ago"

    if hours < 24:
        return f"{hours} hrs ago"

    days = hours // 24

    if days == 1:
        return f"1 day ago"

    return f"{days} days ago"


def get_top_metrics(db: Session) -> dict:
    active_fires = (
        db.query(func.count(FireReports.id))
        .filter(FireReports.status == ReportStatus.verified)
        .scalar()
    )
    pending_approvals = (
        db.query(func.count(RoleRequest.request_id))
        .filter(RoleRequest.status == RequestStatus.pending)
        .scalar()
    )

    total_users = db.query(func.count(User.id)).scalar()

    system_status = "ALERT" if active_fires > 10 else "OKAY"

    return {
        "active_fires": active_fires,
        "pending_approvals": pending_approvals,
        "total_users": total_users,
        "system_status": system_status,
    }


def get_recent_activity(db: Session, limit: int = 7) -> list[dict]:
    recent_fires = (
        db.query(FireReports)
        .order_by(FireReports.submitted_at.desc())
        .limit(limit)
        .all()
    )
    recent_role_requests = (
        db.query(RoleRequest)
        .filter(RoleRequest.reviewed_at.isnot(None))
        .order_by(RoleRequest.reviewed_at.desc())
        .limit(limit)
        .all()
    )
    activity_items = []
    for report in recent_fires:
        activity_items.append(
            {
                "id": f"fire-{report.id}",
                "message": f"New fire reported - {report.location_text}",
                "timeAgo": calculate_time_ago(report.submitted_at),
                "_sort_ts": as_aware(report.submitted_at),
            }
        )

    for rr in recent_role_requests:
        activity_items.append(
            {
                "id": f"role-{rr.request_id}",
                "message": f"Role {rr.status.value} - {rr.user_id} ({rr.requested_role.value})",
                "timeAgo": calculate_time_ago(rr.reviewed_at),
                "_sort_ts": as_aware(rr.reviewed_at),
            }
        )

    activity_log = sorted(
        activity_items,
        key=lambda x: x["_sort_ts"] or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )[:limit]
    for item in activity_log:
        item.pop("_sort_ts", None)

    return activity_log


def get_weekly_incident_counts(db: Session, days: int = 7) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(days=days)

    recent_week_fires = (
        db.query(FireReports).filter(FireReports.submitted_at >= since).all()
    )

    day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    counts_by_day = {day: 0 for day in day_order}
    for report in recent_week_fires:
        day_name = report.submitted_at.strftime("%a")
        if day_name in counts_by_day:
            counts_by_day[day_name] += 1

    weekly_incidents = [{"day": day, "count": counts_by_day[day]} for day in day_order]

    return weekly_incidents


def get_system_metrics(db: Session) -> dict:
    system_metrics = {
        "predictions_completed": 0,
        "model_health": "Unknown",
        "avg_confidence_percent": 0,
        "last_sync_time": "Not yet tracked",
    }

    return system_metrics


def dashboard_summary(db: Session) -> dict:
    return {
        "top_metrics": get_top_metrics(db),
        "activity_log": get_recent_activity(db),
        "weekly_incidents": get_weekly_incident_counts(db),
        "system_metrics": get_system_metrics(db),
    }
