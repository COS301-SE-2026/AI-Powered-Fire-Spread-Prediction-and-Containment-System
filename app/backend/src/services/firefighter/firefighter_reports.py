from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.reported_fires import FireReports
from models.users import User
from geoalchemy2.shape import to_shape

def get_fire_reports(db:Session):
    request = db.query(FireReports).all()

    if not request:
        raise ValueError("No reports have been found")

    formatted = []
    for fire in request:
        shape = to_shape(fire.location_geom)
        formatted.append({
            "reference_number": fire.reference_number,
            "location_text": fire.location_text,
            "status": fire.status,
            "boundary_radius": float(fire.boundary_radius),
            "submitted_at": fire.submitted_at,
            "reporter": fire.reporter,
            "latitude": shape.y,
            "longitude": shape.x
        })

    return { "data": request, "total":len(request)}

def search_report_table(db:Session, key:str):
    request = db.query(FireReports).outerjoin(FireReports.user).filter(or_(FireReports.reference_number.ilike(f"%{key}%"), FireReports.location_text.ilike(f"%{key}%"), User.name.ilike(f"%{key}%"), User.surname.ilike(f"%{key}%"))).all()

    if not request:
        raise ValueError(f"{key} not found")
    
    return { "data": request, "total":len(request)}

def get_single_fire_report(db:Session, ref:str):
    request = db.query(FireReports).filter(FireReports.reference_number == ref).first()

    if not request:
        raise ValueError(f"Requested reference number {ref} does not exist")

    return request

            