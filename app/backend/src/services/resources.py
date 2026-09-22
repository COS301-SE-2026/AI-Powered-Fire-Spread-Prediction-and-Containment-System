# Handles the GET /api/resources (hence not the same as the one in users)

from typing import Optional
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_Distance, ST_X, ST_Y
from geoalchemy2.types import Geography
from sqlalchemy import cast
from sqlalchemy.orm import Session

from app.backend.src.enums.resource import ResourceStatus
from app.backend.src.models.water_resource import WaterResource

def get_nearby_resources(
    db: Session,
    lat: float,
    lng: float,
    radius_km: Optional[float] = None,
    status: Optional[ResourceStatus] = ResourceStatus.available,
) -> dict:
    """Resources near (lat, lng) nearest first"""
    point = WKTElement(f"POINT({lng} {lat})", srid=4326)
    point_geog = cast(point, Geography)
    distance_m = ST_Distance(cast(WaterResource.location_geom, Geography), point_geog)
    
    query = db.query(
        WaterResource,
        distance_m.label("distance_m"),
        ST_Y(WaterResource.location_geom).label("lat"),
        ST_X(WaterResource.location_geom).label("lng"),
    )
    
    if status is not None:
        query = query.filter(WaterResource.status == status)
    if radius_km is not None:
        query = query.filter(distance_m <= radius_km * 1000)
    
    rows = query.order_by(distance_m).all()
    
    data = []
    for resource, dist_m, r_lat, r_lng in rows:
        data.append(
            {
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
                "external_pin": {"lat": r_lat, "lng": r_lng},
                "name": resource.name,
                "contact": resource.contact,
                "distance": round(dist_m / 1000, 2),
            }
        )
    
    return {"data": data, "total": len(data)}
