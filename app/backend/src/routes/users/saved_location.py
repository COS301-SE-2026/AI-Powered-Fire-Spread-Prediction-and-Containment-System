from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.backend.src.db import get_db
from app.backend.src.schemas.saved_location import (
    SavedLocationCreate,
    SavedLocationUpdate,
)
from app.backend.src.services.saved_location import (
    create_saved_location,
    delete_saved_location,
    get_my_saved_locations,
    get_saved_locations,
    update_saved_location,
)
from app.backend.src.services.auth import get_current_user

router = APIRouter(prefix="/api/users/saved-locations", tags=["saved-locations"])

@router.get("")
def list_saved_locations(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_saved_locations(db, user.id)

@router.get("/{location_id}")
def get_saved_location(location_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return get_my_saved_locations(location_id, user.id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("")
def add_saved_location(
    payload: SavedLocationCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        return create_saved_location(payload, user.id, db)
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
        return update_saved_location(location_id, user.id, payload, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.delete("/{location_id}")
def remove_saved_location(location_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try: 
        delete_saved_location(location_id, user.id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"detail": "Saved location deleted"}
