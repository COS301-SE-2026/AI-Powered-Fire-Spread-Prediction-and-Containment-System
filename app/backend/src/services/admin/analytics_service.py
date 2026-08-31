from datetime import datetime, timezone, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from enums.user_role import UserRole
from enums.role_request_status import RequestStatus
from models.reported_fires import FireReports
from models.users import User
from models.role_request import RoleRequest
from schemas.admin_analytics import AnalyticsOverviewResponse, KPIs
from schemas.role_request import RoleRequestResponse, UserSummary


def get_kpis(db: Session) -> KPIs:

    total_users = db.query(User).filter(User.is_active == True).count()

    if not total_users:
        raise ValueError("Unable to get user metrics")

    pending_count = (
        db.query(RoleRequest)
        .filter(RoleRequest.status == RequestStatus.pending)
        .count()
    )
    total_firefighters = (
        db.query(User)
        .filter(User.role == UserRole.firefighter, User.is_active == True)
        .count()
    )
    total_admins = (
        db.query(User)
        .filter(User.role == UserRole.admin, User.is_active == True)
        .count()
    )

    return KPIs(
        total_users=total_users,
        pending_role_requests=pending_count,
        total_firefighters=total_firefighters,
        total_admins=total_admins,
    )


def get_pending_role_reqs(db: Session, limit: int = 20) -> list[RoleRequestResponse]:
    if limit <= 0:
        raise ValueError("limit has to be a positive value")

    pending_requests = (
        db.query(RoleRequest)
        .filter(RoleRequest.status == RequestStatus.pending)
        .order_by(RoleRequest.created_at.desc())
        .limit(limit)
        .all()
    )

    pending_responses = []
    for req in pending_requests:
        user = db.query(User).filter(User.id == req.user_id).first()
        if user:
            pending_responses.append(
                RoleRequestResponse(
                    request_id=req.request_id,
                    user=UserSummary(
                        id=user.id,
                        name=user.name,
                        surname=user.surname,
                        email=user.email,
                        license_number=user.license_number,
                    ),
                    requested_role=req.requested_role,
                    current_role=req.current_role,
                    status=req.status,
                    created_at=req.created_at,
                    reviewed_at=req.reviewed_at,
                    reviewed_by=req.reviewed_by,
                )
            )
    return pending_responses


def analytics_overview(db: Session) -> AnalyticsOverviewResponse:
    return AnalyticsOverviewResponse(
        kpis=get_kpis(db),
        pending_requests=get_pending_role_reqs(db),
    )
