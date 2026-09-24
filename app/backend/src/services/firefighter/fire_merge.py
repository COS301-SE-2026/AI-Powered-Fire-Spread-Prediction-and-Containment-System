# detects when two active, verifies fires have grown close enough to be the 
# same real-world fire and merges newer record into older one

from __future__ import annotations

import math
from datetime import datetime, timezone
from decimal import Decimal

from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from app.backend.src.enums.fire_status import FireStatus, fire_status_severity
from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.models.reported_fires import FireReports
from app.backend.src.services.cache import cache_client
from app.backend.src.services.notifications import notify_fire_update

METERS_PER_DEG_LAT = 111_320.0

# a fire must show as overlapping for this long continuously before actually merged
DEBOUNCE_SECONDS = 3 * 60

NORMAL_CREEP_KM_PER_MIN = 0.002
MAX_GROWTH_KM = 5.0

def estimate_current_radius_km(boundary_radius_km: Decimal, submitted_at: datetime) -> float:
    elapsed_min = max(0.0, (datetime.now(timezone.utc) - submitted_at).total_seconds() / 60.0)
    growth = min(MAX_GROWTH_KM, NORMAL_CREEP_KM_PER_MIN * elapsed_min)
    return float(boundary_radius_km) + growth

def distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    dlat_km = (lat1 - lat2) * (METERS_PER_DEG_LAT / 1000.0)
    dlng_km = (lng1 - lng2) * (METERS_PER_DEG_LAT / 1000.0) * math.cos(math.radians((lat1 + lat2) / 2))
    return math.hypot(dlat_km, dlng_km)

def pair_key(id_a: str, id_b: str) -> str:
    a, b = sorted([id_a, id_b])
    return f"merge:candidate:{a}:{b}"

def is_persistently_overlapping(id_a: str, id_b) -> bool:
    """
    Tracks how long a pair has been continuously overlapping using shared Valkey cache.
    Falls back to merging immidiately if Valkey unreachable rather than silently
    never merging.
    """
    key = pair_key(id_a, id_b)
    if cache_client is None:
        return True
    try:
        first_seen = cache_client.get(key)
        now = datetime.now(timezone.utc).timestamp()
        if first_seen is None:
            cache_client.set(key, str(now), ex=DEBOUNCE_SECONDS * 3)
            return False
        return (now - float(first_seen)) >= DEBOUNCE_SECONDS
    except Exception:
        return True
    
def clear_candidate(id_a: str, id_b: str) -> None:
    if cache_client is None:
        return
    try:
        cache_client.delete(pair_key(id_a, id_b))
    except Exception:
        pass
    
def notify_merge(db: Session, primary: FireReports, secondary: FireReports) -> None:
    try:
        notify_fire_update(
            db, primary, f"{primary.reference_number} fire has grown together with fire {secondary.reference_number}"
        )
        notify_fire_update(
            db, secondary, f"{secondary.reference_number} fire has grown into fire {primary.reference_number} and is now tracked there"
        )
    except Exception:
        pass
    
def merge_pair(db: Session, fire_a: FireReports, fire_b: FireReports) -> None:
    primary, secondary = (fire_a, fire_b) if fire_a.submitted_at <= fire_b.submitted_at else (fire_b, fire_a)
    
    secondary.merged_into_id = primary.id
    if fire_status_severity[secondary.fire_status] > fire_status_severity[primary.fire_status]:
        primary.fire_status = secondary.fire_status
        
    db.commit()
    clear_candidate(fire_a.id, fire_b.id)
    notify_merge(db, primary, secondary)
    
def chaeck_and_merge_active_fires(db: Session) -> None:
    """
    Call this before reading active-fires list. Cheap no-op when there's nothing 
    overlapping. Only touched db when actual merge happens
    """
    active_fires = (
        db.query(FireReports)
        .filter(
            FireReports.status == ReportStatus.verified,
            FireReports.fire_status == FireStatus.active,
            FireReports.merged_into_id.is_(None),
        )
        .all()
    )
    
    if len(active_fires) < 2:
        return
    
    positions = []
    for fire in active_fires:
        shape = to_shape(fire.location_geom)
        radius_km = estimate_current_radius_km(fire.boundary_radius, fire.submitted_at)
        positions.append((fire, shape.y, shape.x, radius_km))
        
    for i in range(len(positions)):
        fire_a, lat_a, lng_a, radius_a = positions[i]
        for j in range(i + 1, len(positions)):
            fire_b, lat_b, lng_b, radius_b = positions[j]
            
            dist_km = distance_km(lat_a, lng_a, lat_b, lng_b)
            if dist_km > (radius_a + radius_b):
                clear_candidate(fire_a.id, fire_b.id)
                continue
            
            if is_persistently_overlapping(fire_a.id, fire_b.id):
                merge_pair(db, fire_a, fire_b)
                return
        
    
