import base64
import math
import zlib
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.backend.src.enums.fire_status import FireStatus
from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.services.firefighter import fire_merge
from app.backend.src.services.firefighter import fire_terrain_bias as ftb
from app.backend.src.services.users import fire_report

# Tesing math
def test_distance_km_is_zero_for_identical_points():
    assert fire_merge.distance_km(-25.75, 28.23, -25.75, 28.23) == pytest.approx(0.0, abs=1e-9)
    
def test_distance_km_is_symmetric():
    d1 = fire_merge.distance_km(-25.75, 28.23, -25.80, 28.30)
    d2 = fire_merge.distance_km(-25.80, 28.30, -25.75, 28.23)
    assert d1 == pytest.approx(d2)
    
def test_distance_km_one_degree_latitude_is_about_111km():
    d = fire_merge.distance_km(-25.0, 28.0, -26.0, 28.0)
    assert d == pytest.approx(111.32, rel=0.01)
    
def test_estimate_current_radius_km_grows_with_elapsed_time():
    now = datetime.now(timezone.utc)
    fresh = fire_merge.estimate_current_radius_km(Decimal("0.5"), now)
    old = fire_merge.estimate_current_radius_km(Decimal("0.5"), now - timedelta(hours=2))
    assert old > fresh
    
def test_estimate_current_radius_km_starts_at_boundary_radius():
    now = datetime.now(timezone.utc)
    radius = fire_merge.estimate_current_radius_km(Decimal("0.5"), now)
    assert radius == pytest.approx(0.5, abs=1e-6)
    
def test_estimate_current_radius_km_is_capped_at_max_growth():
    now = datetime.now(timezone.utc)
    very_old = now - timedelta(days=30)
    radius = fire_merge.estimate_current_radius_km(Decimal("0.5"), very_old)
    assert radius == pytest.approx(0.5 + fire_merge.MAX_GROWTH_KM, abs=1e-6)
    
def test_pair_key_is_order_independent():
    assert fire_merge.pair_key("a", "b") == fire_merge.pair_key("b", "a")
    
def test_pair_key_differs_for_different_pairs():
    assert fire_merge.pair_key("a", "b") != fire_merge.pair_key("a", "c")
    
# Test debounce (is_persistently_overlapping)
@patch("app.backend.src.services.firefighter.fire_merge.cache_client", None)
def test_is_persistently_overlapping_merges_immediately_when_cached_unavailable():
    assert fire_merge.is_persistently_overlapping("a", "b") is True

@patch("app.backend.src.services.firefighter.fire_merge.cache_client")
def test_is_persistently_overlapping_first_sighting_returns_false(mock_cache):
    mock_cache.get.return_value = None
    result = fire_merge.is_persistently_overlapping("a", "b")
    assert result is False
    mock_cache.set.assert_called_once()
    
@patch("app.backend.src.services.firefighter.fire_merge.cache_client")
def test_is_persistently_overlappung_true_once_debounce_elapsed(mock_cache):
    first_seen = datetime.now(timezone.utc).timestamp() - (fire_merge.DEBOUNCE_SECONDS + 10)
    mock_cache.get.return_value = str(first_seen)
    assert fire_merge.is_persistently_overlapping("a", "b") is True
    
@patch("app.backend.src.services.firefighter.fire_merge.cache_client")
def test_is_persistently_overlapping_false_before_debounce_elapsed(mock_cache):
    first_seen = datetime.now(timezone.utc).timestamp() - 5
    mock_cache.get.return_value = str(first_seen)
    assert fire_merge.is_persistently_overlapping("a", "b") is False
    
@patch("app.backend.src.services.firefighter.fire_merge.cache_client")
def test_is_persistently_overlapping_fails_open_on_cache_error(mock_cache):
    mock_cache.get.side_effect = Exception("valkey down")
    assert fire_merge.is_persistently_overlapping("a", "b") is True
    
# Test merge_pair
def make_fire(id, ref, submitted_at, fire_status=FireStatus.active):
    fire = MagicMock()
    fire.id = id
    fire.reference_number = ref
    fire.submitted_at = submitted_at
    fire.fire_status = fire_status
    fire.merged_into_id = None
    return fire

@patch("app.backend.src.services.firefighter.fire_merge.notify_fire_update")
@patch("app.backend.src.services.firefighter.fire_merge.clear_candidate")
def test_merge_older_fire_becomes_primary(mock_clear, mock_notify):
    now = datetime.now(timezone.utc)
    older = make_fire("id-older", "FR-1", now - timedelta(hours=1))
    newer = make_fire("id-newer", "FR-2", now)
    db = MagicMock()
    
    fire_merge.merge_pair(db, newer, older)
    
    assert newer.merged_into_id == "id-older"
    assert older.merged_into_id is None
    db.commit.assert_called_once()
    
@patch("app.backend.src.services.firefighter.fire_merge.notify_fire_update")
@patch("app.backend.src.services.firefighter.fire_merge.clear_candidate")
def test_merge_pair_upgrades_primary_to_more_severe_status(mock_clear, mock_notify):
    now = datetime.now(timezone.utc)
    primary = make_fire("id-a", "FR-1", now - timedelta(hours=1), fire_status=FireStatus.contained)
    secondary = make_fire("id-b", "FR-2", now, fire_status=FireStatus.active)
    db = MagicMock()
    
    fire_merge.merge_pair(db, primary, secondary)
    assert primary.fire_status == FireStatus.active
    
@patch("app.backend.src.services.firefighter.fire_merge.notify_fire_update")
@patch("app.backend.src.services.firefighter.fire_merge.clear_candidate")
def test_merge_pair_never_degrades_primary_status(mock_clear, mock_notify):
    now = datetime.now(timezone.utc)
    primary = make_fire("id-a", "FR-1", now - timedelta(hours=1), fire_status=FireStatus.active)
    secondary = make_fire("id-b", "FR-2", now, fire_status=FireStatus.contained)
    db = MagicMock()
    
    fire_merge.merge_pair(db, primary, secondary)
    assert primary.fire_status == FireStatus.active
    
@patch("app.backend.src.services.firefighter.fire_merge.notify_fire_update")
@patch("app.backend.src.services.firefighter.fire_merge.clear_candidate")
def test_merge_pair_notifies_after_commit_not_before(mock_clear, mock_notify):
    now = datetime.now(timezone.utc)
    primary = make_fire("id-a", "FR-1", now - timedelta(hours=1))
    secondary = make_fire("id-b", "FR-2", now)
    db = MagicMock()
    
    call_order = []
    db.commit.side_effect = lambda: call_order.append("commit")
    mock_notify.side_effect = lambda *a, **kw: call_order.append("notify")
    
    fire_merge.merge_pair(db, primary, secondary)
    assert call_order.index("commit") < call_order.index("notify")
    
# Test check_and_merge_active_fires
def test_check_and_merge_does_nothing_with_fewer_than_two_fires():
    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = []
    fire_merge.check_and_merge_active_fires(db)
    db.commit.assert_not_called()
    
@patch("app.backend.src.services.firefighter.fire_merge.is_persistently_overlapping", return_value=False)
@patch("app.backend.src.services.firefighter.fire_merge.to_shape")
def test_check_and_merge_no_merge_when_fires_are_far_apart(mock_to_shape, mock_overlap):
    now = datetime.now(timezone.utc)
    fire_a = make_fire("id-a", "FR-1", now)
    fire_a.boundary_radius = Decimal("0.1")
    fire_b = make_fire("id-b", "FR-2", now)
    fire_b.boundary_radius = Decimal("0.1")
    
    shape_a, shape_b = MagicMock(y=-25.0, x=28.0), MagicMock(y=-26.0, x=29.0)
    mock_to_shape.side_effect = [shape_a, shape_b]
    
    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = [fire_a, fire_b]
    
    fire_merge.check_and_merge_active_fires(db)
    
    db.commit.assert_not_called()
    mock_overlap.assert_not_called()
    
    @patch("app.backend.src.services.firefighter.fire_merge.merge_pair")
    @patch("app.backend.src.services.firefighter.fire_merge.is_persistently_overlapping", return_value=True)
    @patch("app.backend.src.services.firefighter.fire_merge.to_shape")
    def test_check_and_merges_when_overlapping_and_persistent(mock_to_shape, mock_overlap, mock_merge_pair):
        now = datetime.now(timezone.utc)
        fire_a = make_fire("id-a", "FR-1", now)
        fire_a.boundary_radius = Decimal("5.0")
        fire_b = make_fire("id-b", "FR-2", now)
        fire_b.boundary_radius = Decimal("5.0")
        
        shape = MagicMock(y=-25.0, x=28.0)
        mock_to_shape.side_effect = [shape, shape]
        
        db = MagicMock()
        db.query.return_value.filter.return_value.all.return_value = [fire_a, fire_b]
        
        fire_merge.check_and_merge_active_fires(db)
        mock_merge_pair.assert_called_once_with(db, fire_a, fire_b)

# Test fire_status_change
def make_report(status=ReportStatus.verified, fire_status=FireStatus.active):
    report = MagicMock()
    report.reference_number = "FR-2026-001"
    report.status = status
    report.fire_status = fire_status
    report.containment_percent = None
    return report

@patch("app.backend.src.services.users.fire_report.get_fire_report_by_id", return_value={"stub": True})
@patch("app.backend.src.services.users.fire_report.notify_fire_update")
def test_raises_if_report_not_found(mock_notify, mock_get_by_id):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(ValueError, match="does not exist"):
        fire_report.fire_status_change("FRDOES-NOT-EXIST", FireStatus.contained, None, db)
        
    db.commit.assert_not_called()
    mock_notify.assert_not_called()