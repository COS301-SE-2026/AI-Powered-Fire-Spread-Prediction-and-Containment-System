from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional
from src.models.reported_fires import FireReports
import uuid
from src.enums.report_status import ReportStatus
from src.schemas.fire_report import FireReportCreate

def get_fire_reports(db:Session):
    request = db.query(
        FireReports, 
        func.ST_Y(FireReports.location_geom).label('lat'),
        func.ST_X(FireReports.location_geom).label('lng')
        ).all()
    
    formatted_reports = []
    for report, lat, lng in request:
        formatted_reports.append({
            "reference_number": report.reference_number,
            "user_id": report.user_id,
            "location": report.location_text,
            "description": report.description,
            "lat": lat,
            "lng": lng,
            "status": report.status.value,
            "status_index": report.status_index,
            "submitted_at": report.submitted_at.isoformat()
        })
    return formatted_reports

def create_fire_report(report: FireReportCreate, db:Session, client_ip: str, user_id:Optional[str] = None):
    year = datetime.now().year
    unique_hex = uuid.uuid4().hex[:6].upper()
    reference_num = f"FR-{year}-{unique_hex}"

    point_wkt = f"SRID=4326;POINT({report.lng} {report.lat})"

    new_report = FireReports(
        reference_number=reference_num,
        user_id=user_id,
        reporter_ip=client_ip,
        location_text=report.location_text,
        description=report.description,
        image_url=report.image_url,
        location_geom=point_wkt,
        boundary_radius=report.boundary_radius,
        status=ReportStatus.received,
        status_index=0
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    new_report.lat=report.lat
    new_report.lng=report.lng

    return new_report