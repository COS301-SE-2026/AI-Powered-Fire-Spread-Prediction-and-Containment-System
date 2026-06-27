from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import get_db
from schemas.fire_report import FireReportDetailResponse, FireReportMapResponse
from services.users import fire_report

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/reported-fires", response_model=List[FireReportMapResponse])
def get_reported_fires(db:Session = Depends(get_db)):
    try:
        return fire_report.get_fire_reports(db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/reported-fires/{report_id}", response_model=FireReportDetailResponse)
def get_fire_report_id(report_id: str, db: Session = Depends(get_db)):
    try:
        return fire_report.get_fire_report_by_id(report_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


