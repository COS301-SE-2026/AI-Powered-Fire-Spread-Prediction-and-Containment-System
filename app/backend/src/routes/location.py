from fastapi import APIRouter, Depends
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.dependencies.auth import get_current_user
from app.backend.src.models.users import User
from app.backend.src.schemas.user_location import UserLocationIn
from app.backend.src.services.notifications.notifications import (
    check_proximity_for_user,
)

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.patch("/me/location")
def update_my_location(
    payload: UserLocationIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user.location_geom = from_shape(
        Point(payload.longitude, payload.latitude), srid=4326
    )
    db.commit()
    db.refresh(user)

    check_proximity_for_user(db, user)
    return {"status": "ok"}
