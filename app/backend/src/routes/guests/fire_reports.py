from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.schemas.fire_report import (
    FireReportCreate,
    FireReportDetailResponse,
    FireReportMapResponse,
)
from app.backend.src.services.users import fire_report

router = APIRouter(prefix="/api/guests", tags=["Guests"])


@router.get("/reported-fires", response_model=List[FireReportMapResponse])
def get_reported_fires(
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    return fire_report.get_fire_reports(db, limit=limit, offset=offset)


@router.post("/reported-fires", response_model=FireReportDetailResponse)
def create_fire_report(
    report: FireReportCreate,
    request: Request,
    db: Session = Depends(get_db),
    user_id: Optional[str] = None,
):  # I think we need to still add a different service for guests just not sure what yet
    client_ip = (
        request.client.host
    )  # gets users IP used mainly for guests to be able to see in a way who reported it and to be used to protect against spam
    return fire_report.create_fire_report(report, db, client_ip, user_id)