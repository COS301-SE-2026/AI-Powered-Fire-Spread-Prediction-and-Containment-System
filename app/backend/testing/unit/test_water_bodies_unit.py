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
        
# Test elements_to_geojson
def closed_way(area_side_deg=0.01, lat0=-25.70, lon0=28.20, **tags):
    """A closed way roughly area_side_deg square centered near lat0/lon0"""
    return {
        "type": "way",
        "id": 111,
        "tags": tags,
        "geometry": [
            {"lat": lat0, "lon": lon0},
            {"lat": lat0, "lon": lon0 + area_side_deg},
            {"lat": lat0 + area_side_deg, "lon": lon0 + area_side_deg},
            {"lat": lat0 + area_side_deg, "lon": lon0},
            {"lat": lat0, "lon": lon0},
        ],
    }
    
class TestElementsToGeojson:
    def test_large_reservoir_way_is_included(self):
        el = closed_way(area_side_deg=0.01, name="Klein Dam", water="reservoir")
        result = elements_to_geojson([el], min_area_m2=2000)
        
        assert len(result["features"]) == 1
        feature = result["features"][0]
        assert feature["geometry"]["type"] == "Polygon"
        assert feature["properties"]["name"] == "Klein Dam"
        assert feature["properties"]["source"] == "reservoir"
        assert feature["properties"]["kind"] == "reservoir"
        assert feature["properties"]["areaHa"] > 0
        
    def test_small_pond_below_threshold_is_excluded(self):
        # ~0.0001 deg square is roughly 11mx11m (well under 2000m^2 threshold)
        el = closed_way(area_side_deg=0.0001, name="Tiny puddle", water="pond")
        result = elements_to_geojson([el], min_area_m2=2000)
        assert result["features"] == []
        
    def test_open_way_becomes_dam_wall_linestring(self):
        el = {
            "type": "way",
            "id": 222,
            "tags": {"waterway": "dam", "name": "Main Wall"},
            "geometry": [
                {"lat": -25.70, "lon": 28.20},
                {"lat": -25.701, "lon": 28.201},
            ],
        }
        result = elements_to_geojson([el], min_area_m2=2000)
        
        assert len(result["features"]) == 1
        feature = result["features"][0]
        assert feature["geometry"]["type"] == "LineString"
        assert feature["properties"]["kind"] == "dam_wall"
        assert feature["properties"]["source"] == "dam"
        assert feature["properties"]["name"] == "Main Wall"
        
    def test_node_becomes_point_feature(self):
        el = {
            "type": "node",
            "id": 333,
            "lat": -25.70,
            "lon": 28.20,
            "tags": {"waterway": "dam", "name": "Wall Marker"},
        }
        result = elements_to_geojson([el], min_area_m2=2000)
        
        assert len(result["features"]) == 1
        feature = result["features"][0]
        assert feature["geometry"] == {"type": "Point", "coordinates": [28.20, -25.70]}
        assert feature["properties"]["kind"] == "dam_point"
        
    def test_way_missing_geometry_is_skipped(self):
        el = {"type": "way", "id": 444, "tags": {"water": "reservoir"}}
        result = elements_to_geojson([el], min_area_m2=0)
        assert result["features"] == []
        
    def test_unnamed_feature_has_null_name(self):
        el = closed_way(area_side_deg=0.01, water="reservoir")
        result = elements_to_geojson([el], min_area_m2=2000)
        assert result["features"][0]["properties"]["name"] is None
        
    def test_multiple_elements_produce_multiple_features(self):
        elements = [
            closed_way(area_side_deg=0.01, lon0=28.20, name="Dam A", water="reservoir"),
            closed_way(area_side_deg=0.01, lon0=29.00, name="Dam B", water="reservoir"),
        ]
        result = elements_to_geojson(elements, min_area_m2=2000)
        assert len(result["features"]) == 2
        
# Test GET /api/geo/water-bodies endpoint
VALID_BBOX = dict(min_lat=-26.0, min_lng=28.0, max_lat=-25.9, max_lng=28.1, min_area_m2=2000)

class TestGetWaterBodiesEndpoint:
    def test_rejects_inverted_bbox(self, client):
        params = dict(VALID_BBOX, max_lat=-26.1) #max_lat < min_lat
        resp = client.get("/api/geo/water-bodies", params=params)
        assert resp.status_code == 400
        assert "max_lat/max_lng" in resp.json()["detail"]
        
    def test_rejects_bbox_exceeding_max_side(self, client):
        params = dict(VALID_BBOX, max_lat=VALID_BBOX["min_lat"] + MAX_BBOX_SIDE_DEG + 0.5)
        resp = client.get("/api/geo/water-bodies", params=params)
        assert resp.status_code == 400
        assert "too large" in resp.json()["detail"].lower()
        
    def test_rejects_out_of_range_latitude(self, client):
        params = dict(VALID_BBOX, min_lat=-95.0)
        resp = client.get("/api/geo/water-bodies", params=params)
        assert resp.status_code == 422  # FastAPI query validation (ge=-90)
        
    @patch(f"{MODULE}.query_overpass", new_callable=AsyncMock)
    @patch(f"{MODULE}.cache_client")
    def test_cache_hit_skips_overpass(self, mock_cache, mock_query_overpass, client):
        cached_payload = {
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "properties": {"name": "Cached Dam"}, "geometry": None}],
        }
        mock_cache.get.return_value = json.dumps(cached_payload).encode("utf-8")
        
        resp = client.get("/api/geo/water-bodies", params=VALID_BBOX)
        
        assert resp.status_code == 200
        assert resp.json() == cached_payload
        mock_query_overpass.assert_not_called()
        mock_cache.set.assert_not_called()
        
    @patch(f"{MODULE}.query_overpass", new_callable=AsyncMock)
    @patch(f"{MODULE}.cache_client")
    def test_cache_miss_queries_overpass_and_populates_cache(
        self, mock_cache, mock_query_overpass, client
    ):
        mock_cache.get.return_value = None
        mock_query_overpass.return_value = {
            "elements": [closed_way(area_side_deg=0.01, name="Fresh Dam", water="reservoir")]
        }
        
        resp = client.get("/api/geo/water-bodies", params=VALID_BBOX)
        
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["features"]) == 1
        assert body["features"][0]["properties"]["name"] == "Fresh Dam"
        
        mock_query_overpass.assert_awaited_once()
        mock_cache.set.assert_called_once()
        set_args, set_kwargs = mock_cache.set.call_args
        cache_key_used = set_args[0]
        assert cache_key_used.startswith("geo:water_bodies:")
        assert set_kwargs["ex"] == CACHE_TTL_SECONDS
        
    @patch(f"{MODULE}.query_overpass", new_callable=AsyncMock)
    @patch(f"{MODULE}.cache_client")
    def test_empty_overpass_result_returns_empty_feature_collection(
        self, mock_cache, mock_query_overpass, client
    ):
        mock_cache.get.return_value = None
        mock_query_overpass.return_value = {"elements": []}
        
        resp = client.get("/api/geo/water-bodies", params=VALID_BBOX)
        
        assert resp.status_code == 200
        assert resp.json() == {"type": "FeatureCollection", "features": []}
        
    @patch(f"{MODULE}.query_overpass", new_callable=AsyncMock)
    @patch(f"{MODULE}.cache_client")
    def test_overpass_failure_returns_502(self, mock_cache, mock_query_overpass, client):
        from fastapi import HTTPException
        
        mock_cache.get.return_value = None
        mock_query_overpass.side_effect = HTTPException(
            status_code=502, detail="Overpass query failed: all mirrors down"
        )
        
        resp = client.get("/api/geo/water-bodies", params=VALID_BBOX)
        
        assert resp.status_code == 502
        assert "Overpass query failed" in resp.json()["detail"]
        mock_cache.set.assert_not_called()
        
    @patch(f"{MODULE}.query_overpass", new_callable=AsyncMock)
    @patch(f"{MODULE}.cache_client")
    def test_min_area_filter_is_forwarded_to_overpass_results(
        self, mock_cache, mock_query_overpass, client
    ):
        mock_cache.get.return_value = None
        # one large, one tiny - only large should survive min_area_m2 filter
        mock_query_overpass.return_value = {
            "elements": [
                closed_way(area_side_deg=0.01, lon0=28.20, name="Big Dam", water="reservoir"),
                closed_way(area_side_deg=0.0001, lon0=28.50, name="Small Puddle", water="pond"),
            ]
        }
        
        resp = client.get("/api/geo/water-bodies", params=dict(VALID_BBOX, min_area_m2=2000))
        
        body = resp.json()
        names = [f["properties"]["name"] for f in body["features"]]
        assert names == ["Big Dam"]