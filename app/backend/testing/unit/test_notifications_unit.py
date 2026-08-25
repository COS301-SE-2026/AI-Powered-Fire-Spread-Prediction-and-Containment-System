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

# Geo helpers
class TestHaversineKm:
    def test_same_point_is_zero_distance(self):
        assert haversine_km(-25.75, 28.24, -25.75, 28.24) == pytest.approx(0.0, abs=1e-6)
        
    def test_known_distance_pretoria_to_johannesburg(self):
        # PTA CBD to JHB CBD should be approx 55km
        distance = haversine_km(-25.7461, 28.1881, -26.2041, 28.0473)
        assert distance == pytest.approx(55, abs=5)
        
    def test_distance_is_symmetric(self):
        a_to_b = haversine_km(-25.75, 28.24, -26.20, 28.05)
        b_to_a = haversine_km(-26.20, 28.05, -25.75, 28.24)
        assert a_to_b == pytest.approx(b_to_a, abs=1e9)
        
    def test_antipodal_points_approach_half_earch_circumference(self):
        # A point and its exact  antipode are the max possible distance apart
        distance = haversine_km(0, 0, 0, 180)
        assert distance == pytest.approx(20015, abs=5) # ~half of earth's circumference

class TestPointToLatLng:
    def test_none_geometry_returns_none(self):
        assert point_to_latlng(None) is None
        
    def test_extracts_lat_lng_from_point_geometry(self):
        # test to guard against lat and lng points being accidentlly flipped
        geom = from_shape(Point(28.24, -25.75), srid=4326)
        lat, lng = point_to_latlng(geom)
        assert lat == pytest.approx(-25.75)
        assert lng == pytest.approx(28.24)
        
# Severity derivation
class TestSeverityFromBoundaryRadius:
    def test_zero_radius_is_low(self):
        assert severity_from_boundary_radius(0) == Severity.low
    
    def test_at_low_boundary_is_low(self):
        assert severity_from_boundary_radius(LOW_MAX_KM) == Severity.low
        
    def test_just_above_low_boundary_is_moderate(self):
        assert severity_from_boundary_radius(LOW_MAX_KM + 0.01) == Severity.moderate
        
    def test_at_moderate_boundary_is_moderate(self):
        assert severity_from_boundary_radius(MODERATE_MAX_KM) == Severity.moderate
        
    def test_just_above_moderate_boundary_is_high(self):
        assert severity_from_boundary_radius(MODERATE_MAX_KM + 0.01) == Severity.high
        
    def test_at_high_boundary_is_high(self):
        assert severity_from_boundary_radius(HIGH_MAX_KM) == Severity.high
        
    def test_just_above_high_boundary_is_extreme(self):
        assert severity_from_boundary_radius(HIGH_MAX_KM + 0.01) == Severity.extreme
        
    def test_very_large_radius_is_extreme(self):
        assert severity_from_boundary_radius(1000) == Severity.extreme
        
    def test_accepta_decimal_input(self):
        assert severity_from_boundary_radius(Decimal("3.20")) == Severity.high
        
    def test_accepts_string_input(self):
        # guards against regression if boundary_radius is ever passes through as raw string from request data
        assert severity_from_boundary_radius("1.00") == Severity.moderate
        
# Tier / distance logic
class TestTierForDistance:
    THRESHOLDS = [20.0, 10.0, 5.0]
    
    def test_distance_within_innermost_tier(self):
        # should resolve to smalles tier it qualifies for, not just first threshold it satisfies
        assert tier_for_distance(3.0, self.THRESHOLDS) == 5.0
        
    def test_distance_in_middle_tier(self):
        assert tier_for_distance(8.0, self.THRESHOLDS) == 10.0
    
    def test_distance_in_outer_tier(self):
        assert tier_for_distance(15.0, self.THRESHOLDS) == 20.0

    def test_distance_beyond_all_tiers_returns_none(self):
        assert tier_for_distance(25.0, self.THRESHOLDS) is None
        
    def test_distance_exactly_on_a_threshold_is_inclusive(self):
        assert tier_for_distance(5.0, self.THRESHOLDS) == 5.0
        assert tier_for_distance(10.0, self.THRESHOLDS) == 10.0
        assert tier_for_distance(20.0, self.THRESHOLDS) == 20.0
        
    def test_distance_just_beyond_outermost_threshold(self):
        assert tier_for_distance(20.01, self.THRESHOLDS) is None
        
    def test_zero_distance_resolves_to_innermost_tier(self):
        assert tier_for_distance(0.0, self.THRESHOLDS) == 5.0
        
    def test_empty_thresholds_always_returns_none(self):
        assert tier_for_distance(0.0, []) is None
        
    def test_unordered_thresholds_still_resolve_to_tightest_match(self):
        assert tier_for_distance(3.0, [5.0, 20.0, 10.0])
        
class TestTierThresholdsForRole:
    def test_regular_user_gets_standard_thresholds(self):
        assert tier_thresholds_for_role(UserRole.user) == TIER_THRESHOLDS_KM
    
    def test_admin_gets_staff_thresholds(self):
        assert tier_thresholds_for_role(UserRole.admin) == STAFF_TIER_THRESHOLDS_KM
        
    def test_firefighter_gets_staff_thresholds(self):
        assert tier_thresholds_for_role(UserRole.firefighter) == STAFF_TIER_THRESHOLDS_KM
    
    def test_staff_thresholds_reach_further_than_user_thresholds(self):
        assert max(STAFF_TIER_THRESHOLDS_KM) > max(TIER_THRESHOLDS_KM)
        
class TestDistanceToFireEdge:
    def test_user_outside_boundary_gets_positive_distance(self):
        # ~11.1km apart at equator for 0.1 degree f latitude
        distance = distance_to_fire_edge(0.0, 0.0, 0.1, 0.0, boundary_radius=2.0)
        assert distance == pytest.approx(11.12 - 2.0, abs=0.1)
        
    def test_user_inside_boundary_clamps_to_zero_no_negative(self):
        # center to center dist is small. large boundary_radius shouldn't produce negative "dist to edge"
        distance = distance_to_fire_edge(0.0, 0.0, 0.01, 0.0, boundary_radius=50.0)
        assert distance == 0.0
        
    def test_user_exactly_at_fire_center(self):
        distance = distance_to_fire_edge(-25.75, 28.24, -25.75, 28.24, boundary_radius=1.0)
        assert distance == 0.0
        
    def test_zero_boundary_radius_equals_plain_haversine_distance(self):
        center_distance = haversine_km(-25.75, 28.24, -25.80, 28.30)
        edge_distance = distance_to_fire_edge(-25.75, 28.24, -25.80, 28.30, boundary_radius=0.0)
        assert edge_distance == pytest.approx(center_distance)
        
    def test_accepts_decimal_boundary_radius(self):
        distance = distance_to_fire_edge(0.0, 0.0, 0.1, 0.0, boundary_radius=Decimal("2.00"))
        assert distance == pytest.approx(11.12 - 2.0, abs=0.1)
        
        