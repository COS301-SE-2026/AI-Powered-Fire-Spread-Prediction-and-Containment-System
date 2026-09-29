from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.enums.fire_status import FireStatus
from app.backend.src.enums.user_role import UserRole
from app.backend.src.schemas.fire_report import (
    FireReportDetailResponse,
    FireReportMapResponse,
)
from app.backend.src.services.users import fire_report

from app.backend.src.dependencies.auth import get_current_admin_user
from app.backend.src.dependencies.auth import require_role

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
    dependencies=[Depends(require_role(UserRole.admin, UserRole.firefighter))],
)

dbSession = Annotated[Session, Depends(get_db)]


@router.get("/reported-fires", response_model=List[FireReportMapResponse])
def get_reported_fires(db: dbSession):
    return fire_report.get_fire_reports(db)


@router.get("/reported-fires/{report_ref}", response_model=FireReportDetailResponse)
def get_fire_report_id(report_ref: str, db: dbSession):
    return fire_report.get_fire_report_by_id(report_ref, db)


@router.patch(
    "/reported-fires/{report_ref}/status", response_model=FireReportDetailResponse
)
def status_change(report_ref: str, status: ReportStatus, db: dbSession):
    return fire_report.status_change(report_ref, status, db)

@router.patch(
    "/reported-fires/{report_ref}/fire-status", response_model=FireReportDetailResponse
)
def fire_status_change(
    report_ref: str,
    fire_status: FireStatus,
    db: dbSession,
    containment_percent: float | None = None,
):
    try:
        return fire_report.fire_status_change(report_ref, fire_status, containment_percent, db)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
