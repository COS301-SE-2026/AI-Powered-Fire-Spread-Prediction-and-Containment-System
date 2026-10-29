import os
import time
from pathlib import Path
from unittest.mock import MagicMock, patch
import numpy as np
import pytest
import requests

from app.backend.src.ai.job_builder import (
    DataSourceError,
    fetch_weather_history,
    fetch_static_grids,
    build_volunteer_payload,
    static_cache_path,
    load_static_cache,
    save_static_cache,
    WEATHER_HISTORY_LENGTH,
    DEFAULT_DCA_PARAMS,
)


@pytest.fixture
def mock_job_dict():
    return {
        "grid_h": 10,
        "grid_w": 10,
        "center_lat": -33.9249,
        "center_lon": 18.4241,
        "grid_bounds": [18.40, -33.95, 18.45, -33.90],
    }


def test_fetch_weather_history_success(mock_job_dict):
    n_hours = WEATHER_HISTORY_LENGTH + 1
    mock_hourly_data = {
        "time": [f"2026-10-26T{i:02d}:00" for i in range(n_hours)],
        "temperature_2m": [20.0 + i for i in range(n_hours)],
        "relative_humidity_2m": [50.0 - i for i in range(n_hours)],
        "wind_speed_10m": [5.0 for _ in range(n_hours)],
        "wind_direction_10m": [180.0 for _ in range(n_hours)],
    }

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"hourly": mock_hourly_data}
    mock_resp.raise_for_status = MagicMock()

    with patch("app.backend.src.ai.job_builder._HTTP.get", return_value=mock_resp):
        frames = fetch_weather_history(mock_job_dict)

    assert len(frames) == WEATHER_HISTORY_LENGTH
    first_frame = frames[0]
    assert first_frame["wind_u"].shape == (10, 10)
    assert first_frame["wind_v"].shape == (10, 10)
    assert first_frame["temperature"].shape == (10, 10)
    assert first_frame["rel_humidity"].shape == (10, 10)


def test_fetch_weather_history_insufficient_hours(mock_job_dict):
    mock_hourly_data = {
        "time": ["2026-10-26T00:00"],
        "temperature_2m": [20.0],
        "relative_humidity_2m": [50.0],
        "wind_speed_10m": [5.0],
        "wind_direction_10m": [90.0],
    }

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"hourly": mock_hourly_data}
    mock_resp.raise_for_status = MagicMock()

    with patch("app.backend.src.ai.job_builder._HTTP.get", return_value=mock_resp):
        with pytest.raises(DataSourceError, match="Open-Meteo returned 1 hours, need 6"):
            fetch_weather_history(mock_job_dict)

@pytest.mark.parametrize("exception_cls", [requests.RequestException, ValueError, KeyError])
def test_fetch_weather_history_network_and_parse_errors(mock_job_dict, exception_cls):
    with patch("app.backend.src.ai.job_builder._HTTP.get", side_effect=exception_cls("Network fail")):
        with pytest.raises(DataSourceError, match="Open-Meteo unavailable"):
            fetch_weather_history(mock_job_dict)


def test_static_cache_path(mock_job_dict, monkeypatch, tmp_path):
    monkeypatch.setattr("app.backend.src.ai.job_builder.STATIC_CACHE_DIR", None)
    assert static_cache_path(mock_job_dict) is None

    monkeypatch.setattr("app.backend.src.ai.job_builder.STATIC_CACHE_DIR", str(tmp_path))
    path = static_cache_path(mock_job_dict)
    assert path is not None
    assert path.parent == tmp_path
    assert path.name.startswith("static_")
    assert path.name.endswith(".npz")


def test_load_static_cache_success_and_expiry(tmp_path, monkeypatch):
    cache_file = tmp_path / "valid.npz"
    data = {"elevation": np.ones((5, 5), dtype=np.float32)}
    np.savez_compressed(cache_file, **data)

    monkeypatch.setattr("app.backend.src.ai.job_builder.STATIC_CACHE_TTL_S", 3600)
    loaded = load_static_cache(cache_file)
    assert loaded is not None
    assert np.array_equal(loaded["elevation"], data["elevation"])

    monkeypatch.setattr("app.backend.src.ai.job_builder.STATIC_CACHE_TTL_S", 0)
    assert load_static_cache(cache_file) is None

    assert load_static_cache(None) is None
    assert load_static_cache(tmp_path / "non_existent.npz") is None


def test_load_static_cache_exception_handling(tmp_path):
    corrupted_file = tmp_path / "corrupted.npz"
    corrupted_file.write_bytes(b"corrupted binary data")
    assert load_static_cache(corrupted_file) is None


def test_save_static_cache_success_and_none_path(tmp_path):
    save_static_cache(None, {"test": np.zeros((2, 2))})

    target_path = tmp_path / "subdir" / "cache.npz"
    sample_grids = {"elevation": np.ones((4, 4), dtype=np.float32)}
    save_static_cache(target_path, sample_grids)

    assert target_path.exists()
    with np.load(target_path) as loaded:
        assert "elevation" in loaded.files


def test_save_static_cache_exception_handling(tmp_path):
    bad_path = Path("/invalid_dir_never_created_98765/cache.npz")
    save_static_cache(bad_path, {"test": np.zeros((2, 2))})


def test_fetch_static_grids_cache_hit(mock_job_dict):
    dummy_cached = {"elevation": np.zeros((10, 10), dtype=np.float32)}

    with patch("app.backend.src.ai.job_builder.static_cache_path", return_value=Path("/tmp/fake.npz")), \
         patch("app.backend.src.ai.job_builder.load_static_cache", return_value=dummy_cached):
        result = fetch_static_grids(mock_job_dict)

    assert result is dummy_cached

def test_fetch_static_grids_single_dem_tile():
    mock_job = {
        "grid_h": 10,
        "grid_w": 10,
        "grid_bounds": [18.40, -33.95, 18.45, -33.90],
    }

    dummy_terrain = {
        "elevation": np.zeros((10, 10), dtype=np.float32),
        "slope": np.ones((10, 10), dtype=np.float32),
        "aspect": np.full((10, 10), 45.0, dtype=np.float32),
    }

    dummy_vegetation = {
        "fuel_load": np.full((10, 10), 0.5, dtype=np.float32),
        "dryness": np.full((10, 10), 0.2, dtype=np.float32),
        "nonburnable": np.zeros((10, 10), dtype=np.float32),
    }

    dummy_s2 = MagicMock()
    dummy_s2.b04_path = "/path/b04.tif"
    dummy_s2.b08_path = "/path/b08.tif"
    dummy_s2.b11_path = "/path/b11.tif"
    dummy_s2.scl_path = "/path/scl.tif"

   
    with patch(
        "app.backend.src.ai.job_builder.resolve_dem_path",
        return_value=["/path/single_dem.tif"],
    ), patch(
        "app.backend.src.ai.job_builder.extract_terrain_features",
        return_value=dummy_terrain,
    ), patch(
        "app.backend.src.ai.job_builder.resolve_sentinel2_bands",
        return_value=dummy_s2,
    ), patch(
        "app.backend.src.ai.job_builder.process_sentinal2_and_worldcover",
        return_value=dummy_vegetation,
    ):
        grids = fetch_static_grids(mock_job)

    assert "elevation" in grids
    assert "slope" in grids
    assert "aspect_sin" in grids
    assert "aspect_cos" in grids


def test_fetch_static_grids_multi_dem(mock_job_dict):
    h, w = mock_job_dict["grid_h"], mock_job_dict["grid_w"]

    dummy_terrain = {
        "elevation": np.zeros((h, w), dtype=np.float32),
        "slope": np.ones((h, w), dtype=np.float32),
        "aspect": np.full((h, w), 90.0, dtype=np.float32),
    }

    dummy_vegetation = {
        "fuel_load": np.full((h, w), 0.5, dtype=np.float32),
        "dryness": np.full((h, w), 0.2, dtype=np.float32),
        "nonburnable": np.zeros((h, w), dtype=np.float32),
    }

    dummy_s2 = MagicMock()
    dummy_s2.b04_path = "/path/b04.tif"
    dummy_s2.b08_path = "/path/b08.tif"
    dummy_s2.b11_path = "/path/b11.tif"
    dummy_s2.scl_path = "/path/scl.tif"

    with patch(
        "app.backend.src.ai.job_builder.resolve_dem_path",
        return_value=["/path/dem1.tif", "/path/dem2.tif"],
    ), patch(
        "app.backend.src.ai.job_builder.extract_terrain_features",
        return_value=dummy_terrain,
    ), patch(
        "app.backend.src.ai.job_builder.resolve_sentinel2_bands",
        return_value=dummy_s2,
    ), patch(
        "app.backend.src.ai.job_builder.process_sentinal2_and_worldcover",
        return_value=dummy_vegetation,
    ):
        grids = fetch_static_grids(mock_job_dict)

    assert "elevation" in grids
    assert "aspect_sin" in grids
    assert "aspect_cos" in grids
    assert "fuel_load" in grids
    assert grids["aspect_sin"].shape == (h, w)
    assert grids["aspect_cos"].shape == (h, w)


def test_build_volunteer_payload():
    h, w = 4, 4
    weather_history = [
        {
            "wind_u": np.zeros((h, w), dtype=np.float32),
            "wind_v": np.zeros((h, w), dtype=np.float32),
            "temperature": np.zeros((h, w), dtype=np.float32),
            "rel_humidity": np.zeros((h, w), dtype=np.float32),
        }
    ]

    static_grids = {
        "elevation": np.ones((h, w), dtype=np.float32),
        "slope": np.ones((h, w), dtype=np.float32),
    }

    ignition_mask = np.zeros((h, w), dtype=np.int32)
    grid_bounds = [18.0, -34.0, 18.5, -33.5]
    containment_lines = []

    payload = build_volunteer_payload(
        job_id="test-job-123",
        weather_history=weather_history,
        static_grids=static_grids,
        ignition_mask=ignition_mask,
        cell_size_m=30.0,
        n_steps=60,
        grid_bounds=grid_bounds,
        containment_lines=containment_lines,
    )

    assert payload["job_id"] == "test-job-123"
    assert payload["cell_size_m"] == 30.0

    custom_params = {"a": 0.05, "p_h": 0.1}
    payload_custom = build_volunteer_payload(
        job_id="test-job-456",
        weather_history=weather_history,
        static_grids=static_grids,
        ignition_mask=ignition_mask,
        cell_size_m=30.0,
        n_steps=60,
        grid_bounds=grid_bounds,
        containment_lines=containment_lines,
        params=custom_params,
    )

    assert payload_custom["params"] == custom_params