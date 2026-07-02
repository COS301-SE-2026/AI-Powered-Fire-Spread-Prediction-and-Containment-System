from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from db import get_db
from schemas.firefighter_dashboard import DashboardData
from services.firefighter import firefighter_dashboard

router = APIRouter(prefix="/api/firefighter", tags=["Firefighter"])

# returns nearby fires to location based on the long and lat selected by user or gotten via location aswell as environment variables based on coordinates
@router.get("/firefighter-dashboard", response_model=DashboardData, responses={404: {"description": "No nearby fires found"}})
def get_nearby_fires(lat: float, lng: float, radius_km: float = 20, db: Session=Depends(get_db)):
    try:
        nearby_fires = firefighter_dashboard.get_nearby_fires(db, lat, lng, radius_km)

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    try:
        environment_variables = firefighter_dashboard.get_current_environment_vars(lat, lng)

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    return {"nearby_fires": nearby_fires, "environment_variables": environment_variables}
    
# calculates fire risk still to be implemented
