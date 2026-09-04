from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.schemas.firefighter_reports import (
    FirefighterReportModal,
    FirefighterReportTable,
    ReportList,
)
from app.backend.src.services.firefighter import firefighter_reports

router = APIRouter(prefix="/api/firefighter", tags=["Firefighter"])


# Gets all reported fires to populate the table
@router.get(
    "/reported-fires",
    response_model=ReportList,
    responses={404: {"description": "No fire reports found"}},
)
def get_fire_reports(db: Session = Depends(get_db)):
    try:
        request = firefighter_reports.get_fire_reports(db)

        return request
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


# Search for table
@router.get(
    "/reported-fires/search",
    response_model=ReportList,
    responses={404: {"description": "key is not found"}},
)
def search_location_table(key: str, db: Session = Depends(get_db)):
    try:
        request = firefighter_reports.search_report_table(db, key)

        return request
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


# Gets the data for the single fire view modal
@router.get(
    "/reported-fires/{ref}",
    response_model=FirefighterReportModal,
    responses={404: {"description": "Fire report not found"}},
)
def get_single_fire_report(ref: str, db: Session = Depends(get_db)):
    try:
        request = firefighter_reports.get_single_fire_report(db, ref)

        return request
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
