from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from schemas.firefighter_reports import FirefighterReportTable, ReportList
from services.firefighter import firefighter_reports

router = APIRouter(prefix="/api/firefighter", tags=["Firefighter"])

@router.get("/reported-fires", response_model=FirefighterReportTable)
def get_fire_reports(db:Session = Depends(get_db)):
    return firefighter_reports.get_fire_reports(db)

@router.get("/reported-fires/search/reference", response_model=FirefighterReportTable)
def search_ref_table(ref:str, db:Session = Depends(get_db)):
    return firefighter_reports.get_fire_reports(db, ref)

@router.get("/reported-fires/search/reporter", response_model=FirefighterReportTable)
def search_reporter_table(reporter:str, db:Session = Depends(get_db)):
    return firefighter_reports.get_fire_reports(db, reporter)

@router.get("/reported-fires/search/location", response_model=FirefighterReportTable)
def search_location_table(location:str, db:Session = Depends(get_db)):
    return firefighter_reports.get_fire_reports(db, location)
