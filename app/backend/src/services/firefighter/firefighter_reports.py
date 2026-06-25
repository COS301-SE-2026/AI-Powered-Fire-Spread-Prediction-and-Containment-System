from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date, datetime
from models.firefighter_reports import Firefighter_FireReports
from models.users import User
from enums.firefighter_status import FirefighterReportStatus

def get_fire_reports(db:Session):
    request = db.query(Firefighter_FireReports).all()
    return { "data": request, "total":len(request)}

def search_ref_table(db:Session, ref:str):
    request = db.query(Firefighter_FireReports).filter(Firefighter_FireReports.reference_number.ilike(f"%{ref}%")).all()

    return request

def search_reporter_table(db:Session, reporter:str):
    request = db.query(Firefighter_FireReports).join(or_(Firefighter_FireReports.user).filter(User.name.ilike(f"%{reporter}%"), User.surname.ilike(f"%{reporter}%"))).all()

    return request

def search_location_table(db:Session, location:str):
    request = db.query(Firefighter_FireReports).filter(Firefighter_FireReports.location_text.ilike(f"%{location}%")).all()

    return request
    
            