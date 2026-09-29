from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from app.backend.src.enums.fire_status import FireStatus

NORMAL_CREEP_KM_PER_MIN = 0.002

def estimate_current_radius_km(boundary_radius_km: Decimal | float, submitted_at: datetime) -> float:
    """
    Time-based creep model: fire's radius grows linearly from reported size for as long
    as it's been active with no upper bound. Growth stops only when the caller stops calling this
    for a fire that's no longer active.
    """
    elapsed_min = max(0.0, (datetime.now(timezone.utc) - submitted_at).total_seconds() / 60.0)
    growth = NORMAL_CREEP_KM_PER_MIN * elapsed_min
    return float(boundary_radius_km) + growth

def effective_boundary_radius_km(fire_report) -> float:
    """
    Best current estimate of a fire's boundary radius
    """
    if fire_report.fire_status != FireStatus.active or fire_report.submitted_at is None:
        return float(fire_report.boundary_radius)
    return estimate_current_radius_km(fire_report.boundary_radius, fire_report.submitted_at)