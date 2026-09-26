import uuid
from typing import Optional

from fastapi import HTTPException, status as http_status

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.backend.src.enums.resource import ResourceStatus, capacity_unit_for
from app.backend.src.enums.user_role import UserRole
from app.backend.src.models.users import User
from app.backend.src.models.water_resource import WaterResource
from app.backend.src.schemas.resource import ResourceCreate, ResourceStatusUpdate

def to_response(resource: WaterResource, lat: float, lng: float) -> dict:
    return {
        "id": resource.id,
        "resource": resource.resource_type,
        "other_resource": resource.other_resource or "",
        "capacity": resource.capacity,
        "capacity_unit": resource.capacity_unit,
        "other_capacity": resource.other_capacity_unit or "",
        "status": resource.status,
        "available_from": resource.available_from,
        "available_until": resource.available_until,
        "location": resource.location_text,
        "external_pin": {"lat": lat, "lng": lng},
        "name": resource.name,
        "contact": resource.contact,
    }
    
def create_resource(payload: ResourceCreate, db: Session, user: User) -> dict:
    pin = payload.external_pin
    resource = WaterResource(
        id=str(uuid.uuid4()),
        user_id=user.id,
        resource_type=payload.resource,
        other_resource=payload.other_resource or None,
        capacity=payload.capacity,
        capacity_unit=capacity_unit_for(payload.resource),
        other_capacity_unit=payload.other_capacity or None,
        status=ResourceStatus.available,
        available_from=payload.available_from,
        available_until=payload.available_until,
        location_text=payload.location,
        location_geom=f"SRID=4326;POINT({pin.lng} {pin.lat})",
        name=payload.name,
        contact=payload.contact,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    
    return to_response(resource, pin.lat, pin.lng)

def list_resources(db: Session, user: User, limit: int = 50, offset = 0) -> dict:
    """
    Firefighters and admins see every registered resource, Regular users only see their own.
    """
    query = db.query(WaterResource)
    if user.role not in (UserRole.firefighter, UserRole.admin):
        query = query.filter(WaterResource.user_id == user.id)
        
    total = query.count()
    
    rows = (
        query.with_entities(
            WaterResource,
            func.ST_Y(WaterResource.location_geom).label("lat"),
            func.ST_X(WaterResource.location_geom).label("lng"),
        )
        .order_by(WaterResource.created_at.desc(), WaterResource.id)
        .limit(limit)
        .offset(offset)
        .all()
    )
    
    return {"data": [to_response(r, lat, lng) for r, lat, lng in rows], "total": total}

def update_resource_status(resource_id: str, payload: ResourceStatusUpdate, db: Session, current_user: User, ) -> dict: 
    resource = db.query(WaterResource).filter(WaterResource.id == resource_id).first()
    if resource is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Resource not found")

    if resource.user_id != current_user.id:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Not your resource")

    resource.status = payload.status
    db.commit()
    db.refresh(resource)

    lat, lng = db.query(
        func.ST_Y(WaterResource.location_geom), func.ST_X(WaterResource.location_geom)
    ).filter(WaterResource.id == resource.id).one()

    return to_response(resource, lat, lng)

def get_user_resource(db: Session, user: User, limit: int = 50, offset = 0) -> dict:
    """Always scoped to the current user, regardless of role."""
    query = db.query(WaterResource).filter(WaterResource.user_id == user.id)
         
    total = query.count()
    
    rows = (
        query.with_entities(
            WaterResource,
            func.ST_Y(WaterResource.location_geom).label("lat"),
            func.ST_X(WaterResource.location_geom).label("lng"),
        )
        .order_by(WaterResource.created_at.desc(), WaterResource.id)
        .limit(limit)
        .offset(offset)
        .all()
    )
    
    return {"data": [to_response(r, lat, lng) for r, lat, lng in rows], "total": total}


