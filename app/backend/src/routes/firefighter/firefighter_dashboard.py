from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from db import get_db
from schemas.firefighter_dashboard import NearbyFire, NearbyFiresList, EnvironmentVariables
from services.firefighter import firefighter_dashboard

router = APIRouter(prefix="/api/firefighter", tags=["Firefighter"])

# returns nearby fires to location based on the long and lat selected by user or gotten via location
@router.get("/firefighter-dashboard", response_model=NearbyFiresList, responses={404: {"description": "No nearby fires found"}})
def get_nearby_fires(lat: float, lng: float, radius_km: float = 20, db: Session=Depends(get_db)):
    try:
        request = firefighter_dashboard.get_nearby_fires(db, lat, lng, radius_km)

        return request
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
# calculates fire risk

# gets current environment vars based on long and lat of users
@router.get("/firefighter-dashboard", response_model=EnvironmentVariables, responses={404: {"description": "Failed to find environment variables"}})
def get_current_environment_vars(lat:float, lng: float):
    try:
        request = firefighter_dashboard.get_current_environment_vars(lat, lng)

        return request
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))