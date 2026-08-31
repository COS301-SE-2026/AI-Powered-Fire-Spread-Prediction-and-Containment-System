import math
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from enums.report_status import ReportStatus, status_level
from models.reported_fires import FireReports
from schemas.fire_report import FireReportCreate
from services.storage import get_presigned_url
from services.notifications import notify_fire_alert, notify_fire_update


# this is for hectares takes radius in km
def calc_size(radius: float) -> float:
    radius_m = radius * 1000
    return round((math.pi * radius_m**2) / 10_000, 1)


def get_fire_reports(db: Session, user_id: Optional[str] = None):
    query = db.query(
        FireReports,
        func.ST_Y(FireReports.location_geom).label("lat"),
        func.ST_X(FireReports.location_geom).label("lng"),
    ).outerjoin(FireReports.user)

    if user_id is not None:
        query = query.filter(FireReports.user_id == user_id)

    results = query.all()

    if not results:
        return []

    formatted_reports = []
    for report, lat, lng in results:
        formatted_reports.append(
            {
                "id": report.id,
                "reference_number": report.reference_number,
                "location_text": report.location_text,
                "boundary_radius": report.boundary_radius,
                "user_id": report.user_id,
                "description": report.description,
                "lat": lat,
                "lng": lng,
                "status": report.status.value,
                "submitted_at": report.submitted_at.isoformat(),
                "boundary_radius": float(report.boundary_radius),
                "size": calc_size(float(report.boundary_radius)),
                "verification_notes": report.verification_notes,
                "reporter_name": (
                    f"{report.user.name} {report.user.surname}"
                    if report.user
                    else "Anonymous"
                ),
            }
        )
    return formatted_reports


def get_fire_report_by_id(report_ref: str, db: Session):
    request = (
        db.query(
            FireReports,
            func.ST_Y(FireReports.location_geom).label("lat"),
            func.ST_X(FireReports.location_geom).label("lng"),
        )
        .outerjoin(FireReports.user)
        .filter(FireReports.reference_number == report_ref)
        .first()
    )

    if not request:
        raise ValueError(f"Report with id {report_ref} does not exist")

    report, lat, lng = request
    return {
        "id": report.id,
        "reference_number": report.reference_number,
        "location_text": report.location_text,
        "lat": lat,
        "lng": lng,
        "description": report.description,
        "image_url": get_presigned_url(report.image_url),
        "status": report.status,
        "status_index": report.status_index,
        "boundary_radius": float(report.boundary_radius),
        "size": calc_size(float(report.boundary_radius)),
        "submitted_at": report.submitted_at,
        "reporter_name": (
            f"{report.user.name} {report.user.surname}" if report.user else "Anonymous"
        ),
        "priority": report.priority,
        "system_verified": report.system_verified,
        "verification_notes": report.verification_notes,
    }


def create_fire_report(
    report: FireReportCreate, db: Session, client_ip: str, user_id: Optional[str] = None
):
    year = datetime.now().year
    unique_hex = uuid.uuid4().hex[:6].upper()
    reference_num = f"FR-{year}-{unique_hex}"

    point_wkt = f"SRID=4326;POINT({report.lng} {report.lat})"

    new_report = FireReports(
        id=str(uuid.uuid4()),
        reference_number=reference_num,
        user_id=user_id,
        reporter_ip=client_ip,
        location_text=report.location_text,
        description=report.description,
        image_url=report.image_url,
        photo_hash=report.photo_hash,
        location_geom=point_wkt,
        boundary_radius=report.boundary_radius,
        status=ReportStatus.pending,
        status_index=1,
    )

    db.add(new_report)
    db.commit()

    return get_fire_report_by_id(new_report.reference_number, db)


def status_change(report_ref: str, status: ReportStatus, db: Session):
    report = (
        db.query(FireReports).filter(FireReports.reference_number == report_ref).first()
    )

    if not report:
        raise ValueError(f"Report with id {report_ref} does not exist")

    previous_status = report.status

    report.status = status
    report.status_index = status_level.get(status, 0)
    report.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(report)

    if status == ReportStatus.verified and previous_status != ReportStatus.verifies:
        notify_fire_alert(
            db, report, f"Fire reported at {report.location_text} has been verified"
        )
    elif previous_status == ReportStatus.verified:
        notify_fire_update(db, report, f"Status changed to {status.value}")

    return get_fire_report_by_id(report_ref, db)
