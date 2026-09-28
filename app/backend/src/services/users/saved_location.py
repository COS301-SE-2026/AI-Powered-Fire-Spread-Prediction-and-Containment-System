from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.backend.models.saved_location import SavedLocation
from app.backend.schemas.users.saved_location import (
    SavedLocationCreate,
    SavedLocationResponse,
    SavedLocationUpdate,
)

MAX_SAVED_LOCATIONS = 5

def format_location(location: SavedLocation, lat: Optional[float], lng: Optional[float]):
    return {
        "id": location.id,
        "label": location.label,
        "address": location.address,
        "lat": lat,
        "lng": lng,
        "created_at": location.created_at,
    }

def get_saved_locations(db: Session, user_id: str):
    results = (
        db.query(
            SavedLocation,
            func.ST_Y(SavedLocation.location_geom).label("lat"),
            func.ST_X(SavedLocation.location_geom).label("lng"),
        )
        filter(SavedLocation.user_id == user_id)
        .order_by(SavedLocation.created_at)
        .all()
    )
    return [format_location(location, lat, lng) for location, lat, lng in results]

def get_my_saved_locations(location_id: str, user_id: str, db: Session):
    result = (
        db.query(
            SavedLocation,
            func.ST_Y(SavedLocation.location_geom).label("lat"),
            func.ST_X(SavedLocation.location_geom).label("lng"),
        )
        .filter(SavedLocation.id == location_id, SavedLocation.user_id == user_id)
        .first()
    )
    if not result:
        raise ValueError(f"Saved location {location_id} does not exist")

    location, lat, lng = result
    return _format_location(location, lat, lng)

def create_saved_location(payload: SavedLocationCreate, user_id: str, db: Session):
    count = db.query(SavedLocation).filter(SavedLocation.user_id == user_id).count()
    if count >= MAX_SAVED_LOCATIONS:
        raise ValueError(f"You can save at most {MAX_SAVED_LOCATIONS} locations")

    point_wkt = (
        f"SRID=4326;POINT({payload.lng} {payload.lat})"
        if payload.lat is not None and payload.lng is not None
        else None
    )

    new_location = SavedLocation(
        id=str(uuid.uuid4()),
        user_id=user_id,
        label=payload.label,
        address=payload.address,
        location_geom=point_wkt,
    )

    db.add(new_location)
    db.commit()
    db.refresh(new_location)

    return format_location(new_location, payload.lat, payload.lng)

def update_saved_location(location_id: str, user_id: str, payload: SavedLocationUpdate, db: Session):
    location = (
        db.query(SavedLocation)
        .filter(SavedLocation.id == location_id, SavedLocation.user_id == user_id)
        .first()
    )

    if not location:
        raise ValueError(f"Saved location {location_id} does not exist")

    changes = payload.model_dump(exclude_unset=True)

    if changes.get("label") is not None:
        location.label = changes["label"]
    if changes.get("address") is not None:
        location.address = changes["address"]
    if "lat" in changes or "lng" in changes:
        lat = changes.get("lat")
        lng = changes.get("lng")
        location.location_geom = (
            f"SRID=4326;POINT({lng} {lat})" if lat is not None and lng is not None else None
        )

    db.commit()
    db.refresh(location)

    return get_my_saved_locations(location_id, user_id, db)

def delete_saved_location(location_id: str, user_id: str, db: Session):
    location = (
        db.query(SavedLocation)
        .filter(SavedLocation.id == location_id, SavedLocation.user_id == user_id)
        .first()
    )

    if not location:
        raise ValueError(f"Saved location {location_id} does not exist")

    db.delete(location)
    db.commit()