# Handles the GET /api/resources (hence not the same as the one in users)

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.dependencies.auth import require_role
from app.backend.src.enums.resource import ResourceStatus
from app.backend.src.enums.user_role import UserRole
from app.backend.src.schemas.resource import NearbyResourceListResponse
from app.backend.src.services.resources import get_nearby_resources

router = APIRouter(
    prefix="/api/resources", 
    tags=["Resources"],
    dependencies=[Depends(require_role(UserRole.firefighter, UserRole.admin))],
)


@router.get("", response_model=NearbyResourceListResponse)
def list_nearby_resources(
    lat: Annotated[float, Query(description="User latitude")],
    lng: Annotated[float, Query(description="User longitude")],
    db: Annotated[Session, Depends(get_db)],
    radius_km: Annotated[Optional[float], Query(gt=0)] = None,
    status: ResourceStatus = ResourceStatus.available,
):
    return get_nearby_resources(db, lat, lng, radius_km, status)