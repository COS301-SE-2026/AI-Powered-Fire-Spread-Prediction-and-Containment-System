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
    
# Test cache_key
class TestCacheKey:
    def test_deterministic_for_same_inputs(self):
        key_a = cache_key(-26.0, 28.0, -25.9, 28.1, 2000)
        key_b = cache_key(-26.0, 28.0, -25.9, 28.1, 2000)
        assert key_a == key_b
        
    def test_tiny_bbox_jitter_within_rounding_hits_same_key(self):
        # rounded to 3 decimal places so sub-mm diff shouldn't change key
        key_a = cache_key(-26.00001, 28.00001, -25.9, 28.1, 2000)
        key_b = cache_key(-26.00002, 28.00002, -25.9, 28.1, 2000)
        assert key_a == key_b
        
    def test_different_bbox_produces_different_key(self):
        key_a = cache_key(-26.0, 28.0, -25.9, 28.1, 2000)
        key_b = cache_key(-24.0, 30.0, -23.9, 30.1, 2000)
        assert key_a != key_b
        
    def test_different_min_area_produces_different_key(self):
        key_a = cache_key(-26.0, 28.0, -25.9, 28.1, 2000)
        key_b = cache_key(-26.0, 28.0, -25.9, 28.1, 5000)
        assert key_a != key_b
        
    def test_key_is_namespaced(self):
        key = cache_key(-26.0, 28.0, -25.9, 28.1, 2000)
        assert key.startswith("geo:water_bodies")
        
    def test_int_and_float_args_produce_the_same_key(self):
        key_from_ints = cache_key(-26, 28, -25, 29, 2000)
        key_from_floats = cache_key(-26.0, 28.0, -25.0, 29.0, 2000.0)
        assert key_from_ints == key_from_floats
        
# Test build_query
class TestBuildQuery:
    def test_bbox_is_included(self):
        query = build_query(-26.0, 28.0, -25.9, 28.1)
        assert "-26.0,28.0,-25.9,28.1" in query
        
    def test_includes_reservoir_pond_basin_filter(self):
        query = build_query(-26.0, 28.0, -25.9, 28.1)
        assert 'natural"="water"' in query
        assert "reservoir|pond|basin" in query
        
    def test_includes_landuse_reservoir_filter(self):
        query = build_query(-26.0, 28.0, -25.9, 28.1)
        assert 'landuse"="reservoir"' in query
        
    def test_includes_dam_way_and_node_filters(self):
        query = build_query(-26.0, 28.0, -25.9, 28.1)
        assert 'way["waterway"="dam"]' in query
        assert 'node["waterway"="dam"]' in query