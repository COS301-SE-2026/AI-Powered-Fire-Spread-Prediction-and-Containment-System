"""Rejection checks for fire reports"""

import logging
import os
import httpx
import json

from datetime import datetime, timedelta, timezone

from geoalchemy2.shape import to_shape
from geoalchemy2.functions import ST_DWithin
from geoalchemy2 import Geography

from sqlalchemy import cast, select
from sqlalchemy.orm import Session

from enums.report_status import ReportStatus
from models.reported_fires import FireReports

# to log where something fails
logger = logging.getLogger(__name__)

MAX_REPORT_DURATION = timedelta(days=7)

# "South Africa","boundingbox":["-47.1788335","-22.1250301","16.3335213","38.2898954"]
AREA_BOUNDS = {
    "min_lat": -34.9,
    "max_lat": -22.1250301,
    "min_lng": 16.3335213,
    "max_lng": 32.9,
}

MAPBOX_TILEQUERY_URL = "https://api.mapbox.com/v4/mapbox.mapbox-streets-v8/tilequery"

MAPBOX_TOKEN = os.environ.get("NEXT_PUBLIC_MAPBOX_TOKEN")

# Tolerance radius(m) aroun the queries point. The exact point only is too strict for GPS
RADIUS_METERS = 25

# window within which a second report from same user is a duplicate
DUPLICATE_WINDOW = timedelta(hours=6)
DUPLICATE_RADIUS_METERS = 500

REQUIRED_FIELDS = ("user_id", "location_geom", "submitted_at", "image_url")


class LocationCheckUnavailable(Exception):
    """When on_land can't be determined due to failures."""


def get_report_coordinates(report: FireReports) -> tuple[float, float]:
    "Get lat and lng from report"
    if report.location_geom is None:
        return None
    try:
        point = to_shape(report.location_geom)
    except Exception:
        logger.warning("Failed to parse location_geom for report %s", report.id)
        return None
    return point.y, point.x


def within_boundary(lat: float, lng: float) -> bool:
    """Checks if coordinates is within the systems service area. True if within bounds"""
    lat_result = AREA_BOUNDS["min_lat"] <= lat <= AREA_BOUNDS["max_lat"]
    lng_result = AREA_BOUNDS["min_lng"] <= lng <= AREA_BOUNDS["max_lng"]
    return lat_result and lng_result


def valid_location(lat: float, lng: float) -> bool:
    """Check if coordinate is not (0, 0) default true if not (0, 0)"""
    return not (lat == 0.0 and lng == 0.0)


def on_land(lat: float, lng: float) -> bool:
    """Checks if coordinate is on land using Mapobox Tilequery. True if on land"""
    try:
        response = httpx.get(
            f"{MAPBOX_TILEQUERY_URL}/{lng},{lat}.json",
            params={
                "layers": "water",
                "radius": RADIUS_METERS,
                "access_token": MAPBOX_TOKEN,
            },
            timeout=5.0,
        )
        response.raise_for_status()
        features = response.json().get("features", [])
        return len(features) == 0
    except (httpx.HTTPError, json.JSONDecodeError) as exc:
        logger.warning("on_land check failed for (%s, %s): %s", lat, lng, exc)
        raise LocationCheckUnavailable(f"on_land check failed.") from exc


def valid_timestamp(timestamp: datetime) -> bool:
    """Check if the timestamp is not in future or past"""
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    if timestamp > now:
        return False
    if now - timestamp > MAX_REPORT_DURATION:
        return False
    return True


def duplicate_submission(report: FireReports, session: Session) -> bool:
    """Checks if same user has already submitted a report near the location and time. True if duplicate exists"""

    start_time = report.submitted_at - DUPLICATE_WINDOW
    end_time = report.submitted_at + DUPLICATE_WINDOW

    report_point_wkt = f"SRID=4326;{to_shape(report.location_geom).wkt}"

    query = (
        select(FireReports.id)
        .where(
            FireReports.user_id == report.user_id,
            FireReports.id != report.id,
            FireReports.status != ReportStatus.rejected,
            FireReports.submitted_at >= start_time,
            FireReports.submitted_at <= end_time,
            ST_DWithin(
                cast(FireReports.location_geom, Geography),
                cast(report_point_wkt, Geography),
                DUPLICATE_RADIUS_METERS,
            ),
        )
        .limit(1)
    )

    result = session.execute(query)
    return result.scalar_one_or_none() is not None


def required_fields_present(report: FireReports) -> bool:
    """Check that required fields are present"""
    for field in REQUIRED_FIELDS:
        if getattr(report, field, None) in (None, ""):
            return False
    return True


def rejection_check(report: FireReports, session: Session) -> tuple[bool, str | None]:
    """Runs checks on fire reports. Returns True if passed or False with message"""
    if not required_fields_present(report):
        return False, "missing_required_field"

    coordinates = get_report_coordinates(report)

    if coordinates is None:
        return False, "invalid_location"

    lat, lng = coordinates

    if not valid_location(lat, lng):
        return False, "invalid_location"
    if not within_boundary(lat, lng):
        return False, "outside_boundary"
    if not valid_timestamp(report.submitted_at):
        return False, "invalid_timestamp"
    if not report.image_url:
        return False, "missing_photo"
    if duplicate_submission(report, session):
        return False, "duplicate_submission"

    try:
        if not on_land(lat, lng):
            return False, "location_in_water"
    except LocationCheckUnavailable:
        return False, "manual_review"

    return True, None
