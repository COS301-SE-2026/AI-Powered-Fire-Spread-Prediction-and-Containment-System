from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Annotated
from db import get_db
from schemas.fire_report import FireReportDetailResponse, FireReportMapResponse
from services.users import fire_report
from enums.report_status import ReportStatus 

router = APIRouter(prefix="/api/admin", tags=["Admin"])

dbSession = Annotated[Session, Depends(get_db)]

@router.get("/reported-fires", response_model=List[FireReportMapResponse])
def get_reported_fires(db: dbSession):
    return fire_report.get_fire_reports(db)

@router.get("/reported-fires/{report_id}", response_model=FireReportDetailResponse)
def get_fire_report_id(report_id: str, db: dbSession):
    return fire_report.get_fire_report_by_id(report_id, db)

@router.patch("/reported-fires/{report_id}/status", response_model=FireReportDetailResponse)
def status_change(report_id: str, status: ReportStatus, db:dbSession):
    return fire_report.status_change(report_id, status, db)


