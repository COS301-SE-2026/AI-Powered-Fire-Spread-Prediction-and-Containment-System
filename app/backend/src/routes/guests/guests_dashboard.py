from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from services.guests.guests_dashboard import get_guest_dashboard_data
router = APIRouter(prefix="/api/guests", tags=["Guests"])

@router.get("/dashboard")
def guest_dashboard(
    lat: float = Query(..., description="User latitude"),
    lng: float = Query(..., description="User longitude"),
    radius_km: float=20,
    db: Session = Depends(get_db),
):
    try:
        data=get_guest_dashboard_data(db,lat,lng, radius_km)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return data