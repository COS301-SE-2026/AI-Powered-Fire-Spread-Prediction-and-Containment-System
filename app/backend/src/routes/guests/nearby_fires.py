from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.schemas.notification import NotificationOut
from app.backend.src.schemas.user_location import UserLocationIn
from app.backend.src.services.notifications.notifications import (
    check_proximity_for_guest,
)

router = APIRouter(prefix="/api/guests", tags=["Guests"])


@router.post("/nearby-fires", response_model=list[NotificationOut])
def get_nearby_fires_for_guest(
    payload: UserLocationIn,
    db: Session = Depends(get_db),
):
    """
    Public endpoint: deliberately no get_current_user because they never log in,
    hence no account to authenticate, no persistence here
    """
    return check_proximity_for_guest(db, payload.latitude, payload.longitude)
