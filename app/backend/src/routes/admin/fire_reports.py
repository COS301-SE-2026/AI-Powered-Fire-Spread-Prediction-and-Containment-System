from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from enums.report_status import ReportStatus
from schemas.fire_report import FireReportDetailResponse, FireReportMapResponse
from services.users import fire_report

from dependencies.auth import get_current_admin_user

router = APIRouter(
    prefix="/api/admin", tags=["Admin"], dependencies=[Depends(get_current_admin_user)]
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
