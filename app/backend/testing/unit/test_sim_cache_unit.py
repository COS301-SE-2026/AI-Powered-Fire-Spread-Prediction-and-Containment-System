# Unit tests for the app/backend/src/ai/cache.py

import pytest

from app.backend.src.ai import cache as sim_cache

class FakeHashRedis:
    """Just enought of redis-py for cache.py"""

    def __init__(self):
        self.hashes = {}
        self.expiry = {}

    def hset(self, key, mapping):
        self.hashes[key] = {
            k.encode(): (v if isinstance(v, bytes) else str(v).encode())
            for k, v in mapping.items()
        }

    def expire(self, key, seconds):
        self.expiry[key] = seconds

    def hgetall(self, key):
        return dict(self.hashes.get(key, {}))

@pytest.fixture
def fake_client(monkeypatch):
    client = FakeHashRedis()
    monkeypatch.setattr(sim_cache, "client", client)
    return client

# fire at (-26.0, 28.0); default filter box is +/- 0.15 deg
INSIDE = "LINESTRING(28.00 -26.00, 28.01 -26.01)"
INSIDE_2 = "LINESTRING(27.99 -25.99, 28.00 -26.00)"
OUTSIDE = "LINESTRING(30.00 -20.00, 30.01 -20.01)"

def fire_key(**overrides):
    args = dict(
        ref="FR-1", lat=-26.0, lng=28.0, boundary_radius_m=500.0,
        n_steps=12, cell_size_m=30.0, containment_lines=None,
    )
    args.update(overrides)
    return sim_cache.build_fire_cache_key(**args)

def cluster_key(fires, **overrides):
    args = dict(
        fires=fires, lat=-26.0, lng=28.0, n_steps=12,
        cell_size_m=30.0, extent_buffer_deg=0.2,
    )
    args.update(overrides)
    return sim_cache.build_cluster_cache_key(**args)

def prediction(n_steps=3, h=4, w=5, **extra):
    data = {
        "ref": "FR-1",
        "lat": -26.0,
        "lng": 28.0,
        "history": [[t % 3] * (h * w) for t in range(n_steps)],
        "burned_cells": 7,
        "radius_m": 120.5,
        "truncated": False,
        "lat_extent_deg": 0.1,
        "lon_extent_deg": 0.1,
        "grid_h": h,
        "grid_w": w,
        "cell_size_m": 30.0,
    }
    data.update(extra)
    return data

class TestFilterContainmentLines:
    def test_empty_input(self):
        assert sim_cache.filter_containment_lines(-26.0, 28.0, []) == []

    def test_keeps_nearby_drops_far(self):
        assert sim_cache.filter_containment_lines(-26.0, 28.0, [OUTSIDE, INSIDE]) == [INSIDE]

    def test_skips_blank_and_strips_whitespace(self):
        assert sim_cache.filter_containment_lines(-26.0, 28.0,  ["   ", f"  {INSIDE}  "]) == [INSIDE]

    def test_unparseable_line_is_kept(self):
        assert sim_cache.filter_containment_lines(-26.0, 28.0,  ["not wkt"]) == ["not wkt"]

    def test_result_is_sorted(self):
        result = sim_cache.filter_containment_lines(-26.0, 28.0, [INSIDE, INSIDE_2])
        assert result == sorted([INSIDE, INSIDE_2])

class TestFireCacheKey:
    def test_deterministic_and_prefixed(self):
        assert fire_key() == fire_key()
        assert fire_key().startswith("sim:fire:FR-1:")

    @pytest.mark.parametrize(
        "change",
        [
            {"n_steps": 13},
            {"cell_size_m": 31.0},
            {"boundary_radius_m": 600.0},
            {"model_version": "dca-v2"},
            {"ref": "FR-2"},
        ],
    )

    def test_relevant_inputs_change_key(self, change):
        assert fire_key(**change) != fire_key()

    def test_float_noise_is_rounded_away(self):
        assert fire_key(lat=-26.0 + 1e-9) == fire_key()

    def test_containment_order_does_not_matter(self):
        assert fire_key(containment_lines=[INSIDE, INSIDE_2]) == fire_key(containment_lines=[INSIDE_2, INSIDE])

    def test_far_away_line_does_not_bust_cache(self):
        assert fire_key(containment_lines=[OUTSIDE]) == fire_key()

    def test_nearby_line_changes_key(self):
        assert fire_key(containment_lines=[INSIDE]) != fire_key()

FIRES = [("FR-2", -26.0, 28.0, 500.0), ("FR-1", -26.01, 28.01, 300.0)]

class TestClusterCacheKey:
    def test_fire_order_does_not_matter(self):
        assert cluster_key(FIRES) == cluster_key(list(reversed(FIRES)))

    def test_summary_uses_sorted_refs(self):
        assert cluster_key(FIRES).startswith("sim:cluster:FR-1-FR-2:")

    def test_more_than_three_fires_are_summarized(self):
        fires = [(f"FR-{i}", -26.0, 28.0, 100.0) for i in range(5)]
        assert cluster_key(fires).startswith("sim:cluster:FR-0-FR-1-FR-2+2more:")

    def test_steps_change_key(self):
        assert cluster_key(FIRES, n_steps=24) != cluster_key(FIRES)

class TestFirePredictionCache:
    def test_round_trip(self, fake_client):
        data = prediction()
        sim_cache.cache_prediction("k", data, ttl_seconds=60)

        got = sim_cache.get_cached_prediction("k")

        assert got["history"] == data["history"]
        assert got["n_steps"] == 3
        for field in ("ref", "burned_cells", "radius_m", "truncated", "grid_h", "grid_w", "cell_size_m"):
            assert got[field] == data[field]
        assert fake_client.expiry["k"] == 60

    def test_miss_returns_none(self, fake_client):
        assert sim_cache.get_cached_prediction("missing") is None

    def test_corrupt_entry_returns_none(self, fake_client):
        fake_client.hashes["k"] = {b"meta": b"{not json", b"history": b"x"}
        assert sim_cache.get_cached_prediction("k") is None

    def test_incomplete_payload_is_not_cached_and_does_not_raise(self, fake_client):
        sim_cache.cache_prediction("k", {"history": [[0]]})
        assert "k" not in fake_client.hashes

class TestClusterPredictionCache:
    def test_round_trip(self, fake_client):
        data = prediction(fire_refs=["FR-1", "FR-2"])
        del data["ref"]
        sim_cache.cache_cluster_prediction("c", data, ttl_seconds=1800)
    
        got = sim_cache.get_cached_cluster_prediction("c")
    
        assert got["fire_refs"] == ["FR-1", "FR-2"]
        assert got["history"] == data["history"]
        assert fake_client.expiry["c"] == 1800
    
    def test_miss_returns_none(self, fake_client):
        assert sim_cache.get_cached_cluster_prediction("missing") is None
    
    def test_corrupt_entry_returns_none(self, fake_client):
        fake_client.hashes["c"] = {b"meta": b"[]", b"history": b"not zlib"}
        assert sim_cache.get_cached_cluster_prediction("c") is None
    
    def test_incomplete_payload_is_not_cached(self, fake_client):
        sim_cache.cache_cluster_prediction("c", {"history": [[0]]})
        assert "c" not in fake_client.hashes