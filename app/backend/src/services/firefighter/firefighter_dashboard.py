from datetime import datetime, timezone

from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_Distance, ST_DWithin
from geoalchemy2.shape import to_shape
from geoalchemy2.types import Geography
from sqlalchemy import cast
from sqlalchemy.orm import Session

from app.backend.src.models.reported_fires import FireReports
from app.backend.src.services.firefighter.fuel_conditions import get_fuel_conditions


def calculate_time_ago(
    reported_at: datetime,
) -> str:  # return a string for how long ago fire has been reported
    now = datetime.now(timezone.utc)
    difference = now - reported_at
    minutes = int(difference.total_seconds() // 60)

    if minutes < 1:
        return "just now"
    if minutes < 60:
        return f"{minutes} min ago"

    hours = minutes // 60

    if hours == 1:
        return f"1 hr ago"

    if hours < 24:
        return f"{hours} hrs ago"

    days = hours // 24

    if days == 1:
        return f"1 day ago"

    return f"{days} days ago"


# gets fires within a 20km radius of users current or selected location
def get_nearby_fires(db: Session, lat: float, lng: float, radius_km: float = 20):
    point = WKTElement(f"POINT({lng} {lat})", srid=4326)

    geom_geog = cast(FireReports.location_geom, Geography)
    point_geog = cast(point, Geography)

    request = (
        db.query(FireReports)
        .filter(ST_DWithin(geom_geog, point_geog, radius_km * 1000))
        .add_columns(ST_Distance(FireReports.location_geom, point_geog))
        .order_by(ST_Distance(geom_geog, point_geog))
        .all()
    )  # * 1000 because ST_DWithin uses meters not km

    formatted_result = []
    for fire, distance_m in request:  # distance in meters again
        shape = to_shape(fire.location_geom)
        formatted_result.append(
            {
                "location_text": fire.location_text,
                "distance": round(distance_m / 1000, 1),  # meters to km
                "time_ago": calculate_time_ago(fire.submitted_at),
                "status": fire.status,
                "latitude": shape.y,
                "longitude": shape.x,
            }
        )

    return {"data": formatted_result, "total": len(formatted_result)}


def get_current_environment_vars(lat: float, lng: float) -> dict:
    conditions = get_fuel_conditions(lat, lng)

    return {
        "temperature": conditions["temperature"],
        "humidity": conditions["humidity"],
        "wind": conditions["wind_speed"],
        "wind_dir": conditions["wind_direction"],
        "fire_danger": conditions["fdi_band"],
        "fdi": conditions["fdi"],
        "fdi_color": conditions["fdi_color"],
    }
