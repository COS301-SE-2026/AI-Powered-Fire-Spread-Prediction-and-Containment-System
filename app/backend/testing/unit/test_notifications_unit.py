from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from app.backend.src.enums.notification_type import NotificationType
from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.enums.severity import Severity
from app.backend.src.enums.user_role import UserRole

from app.backend.src.models.reported_fires import FireReports
from app.backend.src.models.users import User

from app.backend.src.services.notifications import notifications as svc
from app.backend.src.services.notifications.geo import haversine_km, point_to_latlng
from app.backend.src.services.notifications.notifications import (
    STAFF_TIER_THRESHOLDS_KM,
    TIER_THRESHOLDS_KM,
    distance_to_fire_edge,
    tier_for_distance,
    tier_thresholds_for_role,
)
from app.backend.src.services.notifications.severity import (
    HIGH_MAX_KM,
    LOW_MAX_KM,
    MODERATE_MAX_KM,
    severity_from_boundary_radius,
)


# Geo helpers
class TestHaversineKm:
    def test_same_point_is_zero_distance(self):
        assert haversine_km(-25.75, 28.24, -25.75, 28.24) == pytest.approx(
            0.0, abs=1e-6
        )

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
        assert distance == pytest.approx(20015, abs=5)  # ~half of earth's circumference


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
        assert (
            tier_thresholds_for_role(UserRole.firefighter) == STAFF_TIER_THRESHOLDS_KM
        )

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
        distance = distance_to_fire_edge(
            -25.75, 28.24, -25.75, 28.24, boundary_radius=1.0
        )
        assert distance == 0.0

    def test_zero_boundary_radius_equals_plain_haversine_distance(self):
        center_distance = haversine_km(-25.75, 28.24, -25.80, 28.30)
        edge_distance = distance_to_fire_edge(
            -25.75, 28.24, -25.80, 28.30, boundary_radius=0.0
        )
        assert edge_distance == pytest.approx(center_distance)

    def test_accepts_decimal_boundary_radius(self):
        distance = distance_to_fire_edge(
            0.0, 0.0, 0.1, 0.0, boundary_radius=Decimal("2.00")
        )
        assert distance == pytest.approx(11.12 - 2.0, abs=0.1)


# Service functions (mock session)
DEFAULT_POINT = from_shape(Point(28.24, -25.75), srid=4326)


def make_user(id, role=UserRole.user, has_location=True):
    return User(
        id=id,
        name="Test",
        surname="User",
        email=f"{id}@test.com",
        id_number="0000000000000",
        role=role,
        location_geom=DEFAULT_POINT if has_location else None,
    )


def make_fire(id="fire-1", status=ReportStatus.verified, boundary_radius=1.0):
    return FireReports(
        id=id,
        reference_number=f"REF-{id}",
        location_text="Test Location",
        location_geom=DEFAULT_POINT,
        boundary_radius=boundary_radius,
        status=status,
    )


def query_mock(*, all_result=None, first_result=None, scalar_result=None):
    """
    Chainable mock supporting .filter().all()/.first()/.scalar()/.distinct().all(),
    matching the query patterns acctually used in notifications.py
    """
    m = MagicMock()
    m.filter.return_value = m
    m.distinct.return_value = m
    m.all.return_value = all_result if all_result is not None else []
    m.first.return_value = first_result
    m.scalar.return_value = scalar_result
    return m


@pytest.fixture(autouse=True)
def patched_push():
    """
    Every test in this section gets push() replaced with a no-op mock.
    None of these should depend on a real event loop or WebSocket connection to run or
    to make assertions
    """
    with patch.object(svc, "push") as mock_push:
        yield mock_push


@pytest.fixture
def db():
    return MagicMock()


class TestNotifyFireAlert:
    def test_returns_empty_list_for_unverified_report(self, db):
        fire = make_fire(status=ReportStatus.pending)
        result = svc.notify_fire_alert(db, fire, "New Fire")
        assert result == []
        db.query.assert_not_called()

    def test_raises_if_fire_has_no_location(self, db):
        fire = make_fire()
        with patch.object(svc, "point_to_latlng", return_value=None):
            with pytest.raises(ValueError):
                svc.notify_fire_alert(db, fire, "New fire")

    def test_notifies_user_within_tier(self, db, patched_push):
        fire = make_fire(boundary_radius=0.0)
        nearby_user = make_user("u1", role=UserRole.user)
        db.query.return_value = query_mock(all_result=[nearby_user])

        with patch.object(
            svc, "point_to_latlng", return_value=(-25.75, 28.24)
        ), patch.object(svc, "distance_to_fire_edge", return_value=3.0):
            created = svc.notify_fire_alert(db, fire, "New fire")

        assert len(created) == 1
        assert created[0].user_id == "u1"
        assert created[0].type == NotificationType.alert
        db.commit.assert_called_once()
        patched_push.assert_called_once_with(created[0])

    def test_skips_user_beyond_all_tiers(self, db):
        fire = make_fire(boundary_radius=0.0)
        far_user = make_user("u1", role=UserRole.user)
        db.query.return_value = query_mock(all_result=[far_user])

        with patch.object(
            svc, "point_to_latlng", return_value=(-25.75, 28.24)
        ), patch.object(svc, "distance_to_fire_edge", return_value=999.0):
            created = svc.notify_fire_alert(db, fire, "New fire")

        assert created == []

    def test_skips_user_with_no_saved_location(self, db):
        fire = make_fire()
        no_location_user = make_user("u1", has_location=False)
        db.query.return_value = query_mock(all_result=[no_location_user])

        created = svc.notify_fire_alert(db, fire, "New fire")

        assert created == []

    def test_admin_gets_wider_radius_than_regular_user(self, db):
        fire = make_fire(boundary_radius=0.0)
        admin = make_user("admin1", role=UserRole.admin)
        regular = make_user("user1", role=UserRole.user)
        db.query.return_value = query_mock(all_result=[admin, regular])

        # 30km beyond regular's outermost tier (20km) but within staff's wider 50km max
        with patch.object(
            svc, "point_to_latlng", return_value=(-25.75, 28.24)
        ), patch.object(svc, "distance_to_fire_edge", return_value=30.0):
            created = svc.notify_fire_alert(db, fire, "New fire")

        notified_ids = {n.user_id for n in created}
        assert notified_ids == {"admin1"}

    def test_message_includes_distance(self, db):
        fire = make_fire(boundary_radius=0.0)
        user = make_user("u1")
        db.query.return_value = query_mock(all_result=[user])

        with patch.object(
            svc, "point_to_latlng", return_value=(-25.75, 28.24)
        ), patch.object(svc, "distance_to_fire_edge", return_value=4.2):
            created = svc.notify_fire_alert(db, fire, "New fire")

        assert "4.2km" in created[0].message


class TestCheckProximityForUser:
    def test_returns_empty_if_user_has_no_location(self, db):
        user = make_user("u1", has_location=False)
        result = svc.check_proximity_for_user(db, user)
        assert result == []
        db.query.assert_not_called()

    def test_first_time_in_range_creates_alert(self, db, patched_push):
        user = make_user("u1")
        fire = make_fire()

        fires_query = query_mock(all_result=[fire])
        distance_query = query_mock(scalar_result=None)

        db.query.side_effect = [fires_query, distance_query]

        with patch.object(
            svc, "point_to_latlng", side_effect=[(-25.75, 28.24), (-25.75, 28.24)]
        ), patch.object(svc, "distance_to_fire_edge", return_value=3.0):
            created = svc.check_proximity_for_user(db, user)

        assert len(created) == 1
        assert created[0].type == NotificationType.alert
        patched_push.assert_called_once()

    def test_moving_into_closer_tier_creates_update(self, db):
        user = make_user("u1")
        fire = make_fire()

        fires_query = query_mock(all_result=[fire])

        # prev notified at 15km (outer 20km tier), now closer
        distance_query = query_mock(scalar_result=15.0)
        db.query.side_effect = [fires_query, distance_query]

        with patch.object(
            svc, "point_to_latlng", side_effect=[(-25.75, 28.24), (-25.75, 28.24)]
        ), patch.object(svc, "distance_to_fire_edge", return_value=3.0):
            created = svc.check_proximity_for_user(db, user)

        assert len(created) == 1
        assert created[0].type == NotificationType.update

    def test_same_tier_as_before_creates_nothing(self, db):
        user = make_user("u1")
        fire = make_fire()

        fires_query = query_mock(all_result=[fire])
        # prev notified at 3.5km, same 5km tier as new dist
        distance_query = query_mock(scalar_result=3.5)
        db.query.side_effect = [fires_query, distance_query]

        with patch.object(
            svc, "point_to_latlng", side_effect=[(-25.75, 28.24), (-25.75, 28.24)]
        ), patch.object(svc, "distance_to_fire_edge", return_value=3.0):
            created = svc.check_proximity_for_user(db, user)

        assert created == []

    def test_moving_to_farther_tier_creates_nothing(self, db):
        user = make_user("u1")
        fire = make_fire()

        fires_query = query_mock(all_result=[fire])

        # was prev in 5km, now only within wider 10km tier (moving way, hence no re-notification)
        distance_query = query_mock(scalar_result=3.0)
        db.query.side_effect = [fires_query, distance_query]

        with patch.object(
            svc, "point_to_latlng", side_effect=[(-25.75, 28.24), (-25.75, 28.24)]
        ), patch.object(svc, "distance_to_fire_edge", return_value=999.0):
            created = svc.check_proximity_for_user(db, user)

        assert created == []

    def test_only_verified_fires_are_considered(self, db):
        user = make_user("u1")
        fires_query = query_mock(all_result=[])
        db.query.side_effect = [fires_query]

        created = svc.check_proximity_for_user(db, user)

        assert created == []
        fires_query.filter.assert_called_once()


class TestNotifyFireUpdate:
    def test_returns_empty_if_no_one_previously_notified(self, db):
        fire = make_fire()
        db.query.return_value = query_mock(all_result=[])

        with patch.object(svc, "point_to_latlng", return_value=(-25.75, 28.24)):
            created = svc.notify_fire_update(db, fire, "Update")

        assert created == []

    def test_notifies_every_previously_tracked_user(self, db, patched_push):
        fire = make_fire()
        user1 = make_user("u1")
        user2 = make_user("u2")

        user_ids_query = query_mock(all_result=[("u1",), ("u2",)])
        users_query = query_mock(all_result=[user1, user2])
        db.query.side_effect = [user_ids_query, users_query]

        with patch.object(
            svc, "point_to_latlng", return_value=(-25.75, 28.24)
        ), patch.object(svc, "distance_to_fire_edge", return_value=2.0):
            created = svc.notify_fire_update(db, fire, "Contained")

        assert len(created) == 2
        assert all(n.type == NotificationType.update for n in created)
        assert patched_push.call_count == 2

    def test_user_with_no_location_still_gets_notified_at_zero_distance(self, db):
        fire = make_fire()
        user = make_user("u1", has_location=False)

        user_ids_query = query_mock(all_result=[("u1",)])
        users_query = query_mock(all_result=[user])
        db.query.side_effect = [user_ids_query, users_query]

        with patch.object(svc, "point_to_latlng") as mock_p2ll:
            mock_p2ll.side_effect = [(-25.75, 28.24), None]
            created = svc.notify_fire_update(db, fire, "Contained")

        assert len(created) == 1
        assert created[0].distance == 0.0
        assert created[0].message == "Contained"

    def test_raises_if_fire_has_no_location(self, db):
        fire = make_fire()
        with patch.object(svc, "point_to_latlng", return_value=None):
            with pytest.raises(ValueError):
                svc.notify_fire_update(db, fire, "Contained")


class TestMarkNotificationRead:
    def test_marks_matching_notification_as_read(self, db):
        notification = MagicMock(read=False)
        db.query.return_value = query_mock(first_result=notification)

        result = svc.mark_notification_read(db, "user1", "notif1")

        assert result is notification
        assert notification.read is True
        db.commit.assert_called_once()

    def test_returns_none_if_not_found(self, db):
        db.query.return_value = query_mock(first_result=None)
        result = svc.mark_notification_read(db, "user1", "nonexistent")
        assert result is None
        db.commit.assert_not_called()


class TestCheckProximityForGuest:
    """
    check_proximity_for_guest is stateless (no user_id, nothing persisted, no push()).
    These tests verify that statelessness alongside actual matching logic since that's the property
    that makes it safe for an unauthenticated caller in first place
    """

    def test_returns_empty_when_no_verified_fires_exist(self, db):
        db.query.return_value = query_mock(all_result=[])
        results = svc.check_proximity_for_guest(db, -25.75, 28.24)
        assert results == []

    def test_fire_within_range_is_returned(self, db):
        fire = make_fire()
        db.query.return_value = query_mock(all_result=[fire])

        with patch.object(
            svc, "point_to_latlng", return_value=(-25.75, 28.24)
        ), patch.object(svc, "distance_to_fire_edge", return_value=3.0):
            results = svc.check_proximity_for_guest(db, -25.75, 28.24)

        assert len(results) == 1
        assert results[0].fireId == fire.id
        assert results[0].distance == 3.0
        assert results[0].type == NotificationType.alert

    def test_fire_beyond_all_tiers_is_excluded(self, db):
        fire = make_fire()
        db.query.return_value = query_mock(all_result=[fire])

        with patch.object(
            svc, "point_to_latlng", return_value=(-25.75, 28.24)
        ), patch.object(svc, "distance_to_fire_edge", return_value=999.0):
            results = svc.check_proximity_for_guest(db, -25.75, 28.24)

        assert results == []

    def test_fire_with_no_location_is_skipped(self, db):
        fire = make_fire()
        db.query.return_value = query_mock(all_result=[fire])

        with patch.object(svc, "point_to_latlng", return_value=None):
            results = svc.check_proximity_for_guest(db, -25.75, 28.24)

        assert results == []

    def test_uses_regular_user_thresholds_not_staff(self, db):
        fire = make_fire()
        db.query.return_value = query_mock(all_result=[fire])

        with patch.object(
            svc, "point_to_latlng", return_value=(-25.75, 28.24)
        ), patch.object(svc, "distance_to_fire_edge", return_value=30.0):
            results = svc.check_proximity_for_guest(db, -25.75, 28.24)

        assert results == []

    def test_multiple_fires_in_range_are_all_returned(self, db):
        fire1 = make_fire(id="fire-1")
        fire2 = make_fire(id="fire-2")
        db.query.return_value = query_mock(all_result=[fire1, fire2])

        with patch.object(
            svc, "point_to_latlng", return_value=(-25.75, 28.24)
        ), patch.object(svc, "distance_to_fire_edge", return_value=3.0):
            results = svc.check_proximity_for_guest(db, -25.75, 28.24)

        assert {r.fireId for r in results} == {"fire-1", "fire-2"}

    def test_id_is_synthesized_and_prefixed(self, db):
        fire = make_fire(id="fire-42")
        db.query.return_value = query_mock(all_result=[fire])

        with patch.object(
            svc, "point_to_latlng", return_value=(-25.75, 28.24)
        ), patch.object(svc, "distance_to_fire_edge", return_value=3.0):
            results = svc.check_proximity_for_guest(db, -25.75, 28.24)

        assert results[0].id == "guest-fire-42"

    def test_message_includes_distance(self, db):
        fire = make_fire()
        db.query.return_value = query_mock(all_result=[fire])

        with patch.object(
            svc, "point_to_latlng", return_value=(-25.75, 28.24)
        ), patch.object(svc, "distance_to_fire_edge", return_value=4.2):
            results = svc.check_proximity_for_guest(db, -25.75, 28.24)

        assert "4.2km" in results[0].message

    def test_nothing_is_predicted(self, db, patched_push):
        fire = make_fire()
        db.query.return_value = query_mock(all_result=[fire])

        with patch.object(
            svc, "point_to_latlng", return_value=(-25.75, 28.24)
        ), patch.object(svc, "distance_to_fire_edge", return_value=3.0):
            svc.check_proximity_for_guest(db, -25.75, 28.24)

        db.add.assert_not_called()
        db.commit.assert_not_called()
        patched_push.assert_not_called()

    def test_result_is_marked_unread(self, db):
        # Meaningless for a guest in practice, but schema requires it and it should default
        # sanely rather than being left underfined
        fire = make_fire()
        db.query.return_value = query_mock(all_result=[fire])

        with patch.object(
            svc, "point_to_latlng", return_value=(-25.75, 28.24)
        ), patch.object(svc, "distance_to_fire_edge", return_value=3.0):
            results = svc.check_proximity_for_guest(db, -25.75, 28.24)

        assert results[0].read is False


class TestMarkAllRead:
    def test_marks_all_unread_and_returns_count(self, db):
        n1, n2 = MagicMock(read=False), MagicMock(read=False)
        db.query.return_value = query_mock(all_result=[n1, n2])

        count = svc.mark_all_read(db, "user1")

        assert count == 2
        assert n1.read is True
        assert n2.read is True
        db.commit.assert_called_once()

    def test_returns_zero_when_nothing_unread(self, db):
        db.query.return_value = query_mock(all_result=[])
        count = svc.mark_all_read(db, "user1")
        assert count == 0
