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
    
    
    