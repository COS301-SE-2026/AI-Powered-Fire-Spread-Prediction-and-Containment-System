from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
import uuid

from db import get_db
from models import FireReportModel, FireReport, FireReportCreate, ReportStatus

router = APIRouter(prefix="/api/reports", tags=["Fire Reports"])

@router.get("", response_model=List[FireReport])
def get_fire_reports(db: Session = Depends(get_db)):
    """Fetch all fire reports and extract Lat/Lng for the frontend map."""
    
    results = db.query(
        FireReportModel,
        func.ST_Y(FireReportModel.location_geom).label('lat'),
        func.ST_X(FireReportModel.location_geom).label('lng') 
    ).all()

    formatted_reports = []
    for report, lat, lng in results:
        formatted_reports.append({
            "reference_number": report.reference_number,
            "user_id": report.user_id,
            "location": report.location_text,
            "description": report.description,
            "lat": lat,
            "lng": lng,
            "boundary_radius_km": report.boundary_radius_km,
            "status": report.status.value,
            "status_index": report.status_index,
            "submitted_at": report.submitted_at.isoformat()
        })
        
    return formatted_reports


@router.post("", response_model=FireReport)
def create_fire_report(report: FireReportCreate, db: Session = Depends(get_db)):
    year = datetime.now().year
    unique_hex = uuid.uuid4().hex[:6].upper()
    ref_num = f"FR-{year}-{unique_hex}"
    
    point_wkt = f"SRID=4326;POINT({report.lng} {report.lat})"

    new_report = FireReportModel(
        reference_number=ref_num,
        user_id=report.user_id,
        location_text=report.location,
        description=report.description,
        location_geom=point_wkt,
        boundary_radius_km=report.boundary_radius_km,
        status=ReportStatus.received,
        status_index=0
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return {
        "reference_number": new_report.reference_number,
        "user_id": new_report.user_id,
        "location": new_report.location_text,
        "description": new_report.description,
        "lat": report.lat,
        "lng": report.lng,
        "boundary_radius_km": new_report.boundary_radius_km,
        "status": new_report.status.value,
        "status_index": new_report.status_index,
        "submitted_at": new_report.submitted_at.isoformat()
    }