import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from app.backend.src.ai.job_builder import (
    fetch_weather_history,
    fetch_static_grids,
    build_volunteer_payload,
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
        with pytest.raises(TypeError):
            fetch_weather_history(mock_job_dict)

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


def test_fetch_static_grids_single_and_multi_dem(mock_job_dict):
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
    assert payload["n_steps"] == 60
    assert payload["params"] == DEFAULT_DCA_PARAMS
    assert isinstance(payload["weather_history"], list)
    assert isinstance(payload["static_grids"]["elevation"], list)
    assert isinstance(payload["ignition_mask"], list)