from geoalchemy2.shape import to_shape
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.backend.src.models.reported_fires import FireReports
from app.backend.src.models.users import User


def get_fire_reports(db: Session):
    request = db.query(FireReports).all()

    if not request:
        raise ValueError("No reports have been found")

    formatted = []
    for fire in request:
        shape = to_shape(fire.location_geom)
        formatted.append(
            {
                "id": fire.id,
                "reference_number": fire.reference_number,
                "location_text": fire.location_text,
                "status": fire.status,
                "boundary_radius": float(fire.boundary_radius),
                "submitted_at": fire.submitted_at,
                "reporter": fire.reporter,
                "verification_notes": fire.verification_notes,
                "lat": shape.y,
                "lng": shape.x,
            }
        )

    return {"data": formatted, "total": len(formatted)}


def search_report_table(db: Session, key: str):
    request = (
        db.query(FireReports)
        .outerjoin(FireReports.user)
        .filter(
            or_(
                FireReports.reference_number.ilike(f"%{key}%"),
                FireReports.location_text.ilike(f"%{key}%"),
                User.name.ilike(f"%{key}%"),
                User.surname.ilike(f"%{key}%"),
            )
        )
        .all()
    )

    if not request:
        raise ValueError(f"{key} not found")

    formatted = []
    for fire in request:
        shape = to_shape(fire.location_geom)
        formatted.append(
            {
                "id": fire.id,
                "reference_number": fire.reference_number,
                "location_text": fire.location_text,
                "status": fire.status,
                "boundary_radius": float(fire.boundary_radius),
                "submitted_at": fire.submitted_at,
                "reporter": fire.reporter,
                "verification_notes": fire.verification_notes,
                "lat": shape.y,
                "lng": shape.x,
            }
        )

    return {"data": formatted, "total": len(formatted)}


def get_single_fire_report(db: Session, ref: str):
    request = db.query(FireReports).filter(FireReports.reference_number == ref).first()

    if not request:
        raise ValueError(f"Requested reference number {ref} does not exist")

    shape = to_shape(request.location_geom)

    return {
        "id": request.id,
        "reference_number": request.reference_number,
        "location_text": request.location_text,
        "status": request.status,
        "boundary_radius": float(request.boundary_radius),
        "submitted_at": request.submitted_at,
        "reporter": request.reporter,
        "description": request.description,
        "image_url": request.image_url,
        "verification_notes": request.verification_notes,
        "lat": shape.y,
        "lng": shape.x,
    }
