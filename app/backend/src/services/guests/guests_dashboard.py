from datetime import datetime, timezone

from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_Distance
from geoalchemy2.shape import to_shape
from geoalchemy2.types import Geography
from sqlalchemy import cast
from sqlalchemy.orm import Session

from models.reported_fires import FireReports
from services.firefighter.firefighter_dashboard import (
    get_current_environment_vars,
)  # im reusing the firefighter weather api, since it saves time


def calculate_time_ago(reported_at: datetime) -> str:
    now = datetime.now(timezone.utc)
    diff = now - reported_at
    minutes = int(diff.total_seconds() // 60)
    if minutes < 1:
        return "just now"
    if minutes < 60:
        return f"{minutes} min ago"
    hours = minutes // 60
    if hours == 1:
        return "1 hr ago"
    if hours < 24:
        return f"{hours} hrs ago"
    days = hours // 24
    if days == 1:
        return "1 day ago"
    return f"{days} days ago"


def get_guest_dashboard_data(
    db: Session, lat: float, lng: float, radius_km: float = 20
):
    point = WKTElement(f"POINT({lng} {lat})", srid=4326)
    point_geog = cast(point, Geography)

    query = (
        db.query(
            FireReports,
            ST_Distance(cast(FireReports.location_geom, Geography), point_geog).label(
                "distance_m"
            ),
        )
        .filter(
            ST_Distance(cast(FireReports.location_geom, Geography), point_geog)
            <= radius_km * 1000
        )
        .order_by(ST_Distance(cast(FireReports.location_geom, Geography), point_geog))
        .all()
    )

    nearby = []
    for fire, dist_m in query:
        shape = to_shape(fire.location_geom)
        nearby.append(
            {
                "id": fire.id,
                "reference_number": fire.reference_number,
                "location_text": fire.location_text,
                "lat": shape.y,
                "lng": shape.x,
                "status": fire.status.value,
                "boundary_radius": fire.boundary_radius,  # in km
                "distance": round(dist_m / 1000, 1),  # km
                "time_ago": calculate_time_ago(fire.submitted_at),
            }
        )

    try:
        env = get_current_environment_vars(lat, lng)
    except Exception:
        env = None
    return {
        "nearby_reports": nearby,
        "environment_variables": env,
    }
