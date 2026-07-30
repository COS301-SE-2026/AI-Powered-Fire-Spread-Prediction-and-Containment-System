from datetime import datetime
from typing import Annotated, List

from db import get_db
from enums.role_request_status import RequestStatus
from enums.user_role import UserRole
from fastapi import APIRouter, Depends, HTTPException
from models.role_request import RoleRequest
from models.users import User
from pydantic import BaseModel
from schemas.admin_analytics import AnalyticsOverviewResponse, KPIs
from schemas.role_request import RoleRequestList, RoleRequestResponse, UserSummary
from schemas.user import UserResponse
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/admin/analytics", tags=["Admin Analytics"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(db: Annotated[Session, Depends(get_db)]):
    total_users = db.query(User).filter(User.is_active == True).count()
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
    total_users = db.query(User).filter(User.is_active == True).count()
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
    kpis = KPIs(
        total_users=total_users,
        pending_role_requests=pending_count,
        total_firefighters=total_firefighters,
        total_admins=total_admins,
    )

    pending_requests = (
        db.query(RoleRequest)
        .filter(RoleRequest.status == RequestStatus.pending)
        .order_by(RoleRequest.created_at.desc())
        .limit(20)
        .all()
    )


    pending_requests = (
        db.query(RoleRequest)
        .filter(RoleRequest.status == RequestStatus.pending)
        .order_by(RoleRequest.created_at.desc())
        .limit(20)
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
    return AnalyticsOverviewResponse(
        kpis=kpis,
        pending_requests=pending_responses,
    )

