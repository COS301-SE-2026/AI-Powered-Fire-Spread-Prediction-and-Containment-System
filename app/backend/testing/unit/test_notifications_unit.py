from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from src.enums.notification_type import NotificationType
from src.enums.report_status import ReportStatus
from src.enums.severity import Severity
from src.enums.user_role import UserRole

from src.models.reported_fires import FireReports
from src.models.users import User

from src.services.notifications import notifications as svc
from src.services.notifications.geo import haversine_km, point_to_latlng
from src.services.notifications.notifications import (
    STAFF_TIER_THRESHOLDS_KM,
    TIER_THRESHOLDS_KM,
    distance_to_fire_edge,
    tier_for_distance,
    tier_thresholds_for_role,
)
from src.services.notifications.severity import (
    HIGH_MAX_KM,
    LOW_MAX_KM,
    MODERATE_MAX_KM,
    severity_from_boundary_radius,
)