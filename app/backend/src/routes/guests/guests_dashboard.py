from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from db import get_db
from services.guests.guests_dashboard import get_guest_dashboard_data

router = APIRouter(prefix="/api/guests", tags=["Guests"])


@router.get(
    "/dashboard",
    responses={
        500: {"description": "Internal server error while fetching dashboard data"}
    },
)
def guest_dashboard(
    lat: Annotated[float, Query(description="User latitude")],
    lng: Annotated[float, Query(description="User longitude")],
    db: Annotated[Session, Depends(get_db)],
    radius_km: float = 20,
):
    try:
        data = get_guest_dashboard_data(db, lat, lng, radius_km)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return data
