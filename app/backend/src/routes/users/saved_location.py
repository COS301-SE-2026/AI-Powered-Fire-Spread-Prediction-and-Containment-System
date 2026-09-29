from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.dependencies.auth import get_current_user
from app.backend.src.schemas.saved_locations import (
    SavedLocationCreate,
    SavedLocationUpdate,
)
from app.backend.src.services.users import saved_location as saved_location_service

router = APIRouter(prefix="/api/users/saved-locations", tags=["saved-locations"])

@router.get("")
def list_saved_locations(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return saved_location_service.get_saved_locations(db, user.id)

@router.get("/{location_id}")
def get_saved_location(location_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return saved_location_service.get_my_saved_locations(location_id, user.id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("")
def add_saved_location(
    payload: SavedLocationCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        return saved_location_service.create_saved_location(payload, user.id, db)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.patch("/{location_id}")
def edit_saved_location(
    location_id: str,
    payload: SavedLocationUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        return saved_location_service.update_saved_location(location_id, user.id, payload, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.delete("/{location_id}")
def remove_saved_location(location_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try: 
        saved_location_service.delete_saved_location(location_id, user.id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"detail": "Saved location deleted"}
