import os
import redis
import pytest
import numpy as np

import app.backend.src.ai.cache as cache_module
from app.backend.src.ai.cache import (
    filter_containment_lines,
    build_fire_cache_key,
    get_cached_prediction,
    cache_prediction,
    build_cluster_cache_key,
    get_cached_cluster_prediction,
    cache_cluster_prediction,
)

@pytest.fixture(scope="session", autouse=True)
def configure_test_valkey_client():
    """Ensure client targets a reachable host and port during local test runs."""
    host = os.getenv("VALKEY_HOST", "localhost")
    port = int(os.getenv("VALKEY_PORT", 6379))
    cache_module.client = redis.Redis(host=host, port=port, db=0)

@pytest.fixture(autouse=True)
def clean_valkey_keys():
    """Ensure test keys are wiped before and after each integration test."""
    try:
        keys = cache_module.client.keys("sim:*")
        if keys:
            cache_module.client.delete(*keys)
    except Exception:
        pass
    yield
    try:
        keys = cache_module.client.keys("sim:*")
        if keys:
            cache_module.client.delete(*keys)
    except Exception:
        pass


class TestContainmentLineFiltering:
    def test_filter_containment_lines_intersection_and_whitespace(self):
        lat, lng = -25.7479, 28.2293
        valid_line = "LINESTRING(28.22 -25.74, 28.23 -25.75)"
        outside_line = "LINESTRING(30.00 -30.00, 30.10 -30.10)"
        malformed_line = "NOT_A_VALID_WKT_STRING"
        lines = [
            "   ",  
            valid_line,
            outside_line,
            malformed_line,
        ]
        filtered = filter_containment_lines(lat, lng, lines, extent_buffer_deg=0.15)

        assert valid_line in filtered
        assert malformed_line in filtered
        assert outside_line not in filtered

    def test_filter_containment_lines_empty_list(self):
        assert filter_containment_lines(-25.0, 28.0, []) == []


class TestSingleFireCacheIntegration:
    def test_build_fire_cache_key_deterministic(self):
        k1 = build_fire_cache_key(
            ref="FR-001",
            lat=-25.747912,
            lng=28.229314,
            boundary_radius_m=150.254,
            n_steps=5,
            cell_size_m=30.0,
            containment_lines=["LINESTRING(28.22 -25.74, 28.23 -25.75)"],
        )
        k2 = build_fire_cache_key(
            ref="FR-001",
            lat=-25.747912,
            lng=28.229314,
            boundary_radius_m=150.254,
            n_steps=5,
            cell_size_m=30.0,
            containment_lines=["LINESTRING(28.22 -25.74, 28.23 -25.75)"],
        )
        assert k1.startswith("sim:fire:FR-001:")
        assert k1 == k2

    def test_cache_prediction_and_retrieval_roundtrip(self):
        key = "sim:fire:FR-TEST-01:integration"
        grid_h, grid_w, n_steps = 4, 4, 3

        history = [
            np.arange(grid_h * grid_w, dtype=np.int64).tolist()
            for _ in range(n_steps)
        ]

        payload = {
            "ref": "FR-TEST-01",
            "lat": -25.7479,
            "lng": 28.2293,
            "burned_cells": 12,
            "radius_m": 150.0,
            "truncated": False,
            "lat_extent_deg": 0.05,
            "lon_extent_deg": 0.05,
            "grid_h": grid_h,
            "grid_w": grid_w,
            "cell_size_m": 30.0,
            "history": history,
        }

        assert get_cached_prediction(key) is None

        cache_prediction(key, payload, ttl_seconds=60)

        cached = get_cached_prediction(key)
        assert cached is not None
        assert cached["ref"] == "FR-TEST-01"
        assert cached["n_steps"] == n_steps
        assert len(cached["history"]) == n_steps
        assert cached["history"][0] == history[0]

        ttl = cache_module.client.ttl(key)
        assert 0 < ttl <= 60

    def test_get_cached_prediction_corrupted_data_returns_none(self):
        key = "sim:fire:FR-CORRUPT:integration"
        cache_module.client.hset(key, mapping={"meta": "invalid-json", "history": b"bad-bytes"})
        assert get_cached_prediction(key) is None

    def test_cache_prediction_exception_handling(self):
        key = "sim:fire:FR-ERR:integration"
        bad_payload = {"history": "not-a-valid-array-structure"}
        cache_prediction(key, bad_payload)


class TestClusterCacheIntegration:
    def test_build_cluster_cache_key_formatting_and_summary(self):
        fires_short = [("FR-1", -25.0, 28.0, 100.0), ("FR-2", -25.1, 28.1, 150.0)]
        k1 = build_cluster_cache_key(
            fires=fires_short,
            lat=-25.05,
            lng=28.05,
            n_steps=4,
            cell_size_m=30.0,
            extent_buffer_deg=0.2,
        )
        assert k1.startswith("sim:cluster:FR-1-FR-2:")

        fires_long = [
            ("FR-A", -25.0, 28.0, 100.0),
            ("FR-B", -25.1, 28.1, 150.0),
            ("FR-C", -25.2, 28.2, 200.0),
            ("FR-D", -25.3, 28.3, 250.0),
        ]
        k2 = build_cluster_cache_key(
            fires=fires_long,
            lat=-25.15,
            lng=28.15,
            n_steps=4,
            cell_size_m=30.0,
            extent_buffer_deg=0.2,
        )
        assert "FR-A-FR-B-FR-C+1more" in k2

    def test_cache_cluster_prediction_roundtrip(self):
        key = "sim:cluster:FR-CL-01:integration"
        grid_h, grid_w, n_steps = 3, 3, 2

        history = [
            np.ones((grid_h, grid_w), dtype=np.int64).flatten().tolist()
            for _ in range(n_steps)
        ]

        payload = {
            "fire_refs": ["FR-01", "FR-02"],
            "lat": -25.75,
            "lng": 28.25,
            "burned_cells": 6,
            "radius_m": 250.0,
            "truncated": False,
            "lat_extent_deg": 0.1,
            "lon_extent_deg": 0.1,
            "grid_h": grid_h,
            "grid_w": grid_w,
            "cell_size_m": 30.0,
            "history": history,
        }

        assert get_cached_cluster_prediction(key) is None

        cache_cluster_prediction(key, payload, ttl_seconds=120)

        cached = get_cached_cluster_prediction(key)
        assert cached is not None
        assert cached["fire_refs"] == ["FR-01", "FR-02"]
        assert cached["n_steps"] == n_steps
        assert cached["history"][0] == history[0]

    def test_get_cached_cluster_prediction_corrupted_data_returns_none(self):
        key = "sim:cluster:FR-CORRUPT:integration"
        cache_module.client.hset(key, mapping={"meta": b"bad-json", "history": b"bad-zlib"})
        assert get_cached_cluster_prediction(key) is None

    def test_cache_cluster_prediction_exception_handling(self):
        key = "sim:cluster:FR-FAIL:integration"
        bad_payload = {"history": None}
        cache_cluster_prediction(key, bad_payload)
