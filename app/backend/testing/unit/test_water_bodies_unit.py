import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.backend.main import app
from app.backend.src.routes.geo.water_bodies import (
    CACHE_TTL_SECONDS,
    MAX_BBOX_SIDE_DEG,
    build_query,
    cache_key,
    elements_to_geojson,
    planar_area_m2,
)

MODULE = "app.backend.src.routes.geo.water_bodies"

@pytest.fixture
def client():
    return TestClient(app)

# Test planar_area_m2
class TestPlanarAreaM2:
    def test_degenerate_polygon_returns_zero(self):
        assert planar_area_m2([(0.0, 0.0), (0.01, 0.0)], ref_lat=0.0) == 0.0
        
    def test_known_square_area_at_equator(self):
        # ~0.01 deg square at the equator where 1 deg +- 111.320m in both directions
        coords = [
            (0.0, 0.0),
            (0.01, 0.0),
            (0.01, 0.01),
            (0.0, 0.01),
            (0.0, 0.0),
        ]
        area_m2 = planar_area_m2(coords, ref_lat=0.0)
        expected = (0.01 * 111_320) ** 2
        assert area_m2 == pytest.approx(expected, rel=0.01)
        
    def test_area_shrinks_at_higher_latitude(self):
        # Same deg-square footprint but lng deg are shorter further from equator,
        # so computed area should be smaller.
        coords = [
            (0.0, 0.0),
            (0.01, 0.0),
            (0.01, 0.01),
            (0.0, 0.01),
            (0.0, 0.0),
        ]
        area_equator = planar_area_m2(coords, ref_lat=0.0)
        area_high_lat = planar_area_m2(coords, ref_lat=60.0)
        assert area_high_lat < area_equator
    