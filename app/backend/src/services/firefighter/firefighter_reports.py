from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date, datetime
from models.firefighter_reports import Firefighter_FireReports
from models.users import User
from enums.firefighter_status import FirefighterReportStatus

def get_fire_reports(db:Session):
    request = db.query(Firefighter_FireReports).all()

    if not request:
        raise ValueError("No reports have been found")

    return { "data": request, "total":len(request)}

def search_report_table(db:Session, key:str):
    request = db.query(Firefighter_FireReports).outerjoin(Firefighter_FireReports.user).filter(or_(Firefighter_FireReports.reference_number.ilike(f"%{key}%"), Firefighter_FireReports.location_text.ilike(f"%{key}%"), User.name.ilike(f"%{key}%"), User.surname.ilike(f"%{key}%"))).all()

    if not request:
        raise ValueError(f"{key} not found")
    
    return request

def get_single_fire_report(db:Session, ref:str):
    request = db.query(Firefighter_FireReports).filter(Firefighter_FireReports.reference_number == ref).first()

    if not request:
        raise ValueError(f"Requested reference number {ref} does not exist")

    return request

            