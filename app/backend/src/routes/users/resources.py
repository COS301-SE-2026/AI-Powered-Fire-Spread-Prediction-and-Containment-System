from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.dependencies.auth import get_current_user
from app.backend.src.models.users import User
from app.backend.src.schemas.resource import (
    ResourceCreate,
    ResourceListResponse,
    ResourceResponse,
)
from app.backend.src.services.users import resource as resource_service

router = APIRouter(prefix="/api/users", tags=["Resources"])

@router.post("/resources", response_model=ResourceResponse, status_code=201)
def register_resource(
    payload: ResourceCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return resource_service.create_resource(payload, db, current_user)

@router.get("/resources", response_model=ResourceListResponse)
def get_resources(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return resource_service.list_resources(db, current_user, limit, offset)