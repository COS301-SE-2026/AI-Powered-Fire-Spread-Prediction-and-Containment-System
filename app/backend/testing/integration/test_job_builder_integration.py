from __future__ import annotations

import json
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import requests

import app.backend.src.ai.job_builder as jb
from app.backend.src.ai.job_builder import (
    DEFAULT_DCA_PARAMS,
    DataSourceError,
    build_volunteer_payload,
    fetch_static_grids,
    fetch_weather_history,
    http_session,
    load_static_cache,
    save_static_cache,
    static_cache_path,
)


@pytest.fixture
def sample_job():
    return {
        "grid_bounds": [18.40, -33.95, 18.45, -33.90],
        "grid_h": 8,
        "grid_w": 8,
        "center_lat": -33.925,
        "center_lon": 18.425,
    }


class TestHttpSession:
    def test_http_session_creation(self):
        session = http_session()
        assert isinstance(session, requests.Session)
        adapter = session.adapters.get("https://")
        assert adapter is not None
        assert adapter.max_retries.total == 2


class TestStaticCacheLifecycle:
    def test_static_cache_path_when_dir_none(self, monkeypatch, sample_job):
        monkeypatch.setattr(jb, "STATIC_CACHE_DIR", None)
        assert static_cache_path(sample_job) is None

    def test_static_cache_path_when_dir_set(self, monkeypatch, tmp_path: Path, sample_job):
        monkeypatch.setattr(jb, "STATIC_CACHE_DIR", str(tmp_path))
        path = static_cache_path(sample_job)
        assert path is not None
        assert path.parent == tmp_path
        assert path.name.startswith("static_")
        assert path.suffix == ".npz"

    def test_save_and_load_static_cache_hit(self, tmp_path: Path):
        cache_file = tmp_path / "cache" / "test_static.npz"
        data = {
            "elevation": np.full((4, 4), 100.0, dtype=np.float32),
            "slope": np.full((4, 4), 5.0, dtype=np.float32),
        }

        save_static_cache(cache_file, data)
        assert cache_file.exists()

        loaded = load_static_cache(cache_file)
        assert loaded is not None
        assert "elevation" in loaded
        assert np.array_equal(loaded["elevation"], data["elevation"])
        assert np.array_equal(loaded["slope"], data["slope"])

    def test_save_static_cache_none_path_noop(self):
        save_static_cache(None, {"data": np.zeros(2)})

    def test_save_static_cache_exception_handling(self, tmp_path: Path):
        unwritable_path = tmp_path / "not_a_dir" / "cache.npz"
        with patch.object(Path, "mkdir", side_effect=OSError("Disk error")):
            save_static_cache(unwritable_path, {"test": np.zeros(2)})

    def test_load_static_cache_none_or_missing_or_expired(self, tmp_path: Path, monkeypatch):
        assert load_static_cache(None) is None

        missing_file = tmp_path / "missing.npz"
        assert load_static_cache(missing_file) is None

        expired_file = tmp_path / "expired.npz"
        save_static_cache(expired_file, {"a": np.zeros(2)})
        monkeypatch.setattr(jb, "STATIC_CACHE_TTL_S", 1)
        with patch("time.time", return_value=time.time() + 100):
            assert load_static_cache(expired_file) is None

    def test_load_static_cache_corrupted_file_fallback(self, tmp_path: Path):
        corrupt_file = tmp_path / "corrupt.npz"
        corrupt_file.write_bytes(b"corrupt non-zip data")
        assert load_static_cache(corrupt_file) is None


class TestFetchWeatherHistory:
    def test_fetch_weather_history_success(self, sample_job):
        n_times = 10
        mock_hourly = {
            "time": [f"2026-10-27T{i:02d}:00" for i in range(n_times)],
            "temperature_2m": [20.0 + i for i in range(n_times)],
            "relative_humidity_2m": [50.0 - i for i in range(n_times)],
            "wind_speed_10m": [5.0] * n_times,
            "wind_direction_10m": [90.0] * n_times,
        }

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"hourly": mock_hourly}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(jb._HTTP, "get", return_value=mock_resp):
            frames = fetch_weather_history(sample_job)

        assert len(frames) == jb.WEATHER_HISTORY_LENGTH
        h, w = sample_job["grid_h"], sample_job["grid_w"]
        for f in frames:
            assert f["wind_u"].shape == (h, w)
            assert f["wind_v"].shape == (h, w)
            assert f["temperature"].shape == (h, w)
            assert f["rel_humidity"].shape == (h, w)
            # 90 degrees bearing: wind_u = -speed * sin(90) = -5.0, wind_v = -speed * cos(90) = 0.0
            assert np.isclose(f["wind_u"][0, 0], -5.0)
            assert np.isclose(f["wind_v"][0, 0], 0.0, atol=1e-5)

    def test_fetch_weather_history_insufficient_records_raises_datasource_error(self, sample_job):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "hourly": {
                "time": ["2026-10-27T01:00"],
                "temperature_2m": [20.0],
                "relative_humidity_2m": [50.0],
                "wind_speed_10m": [5.0],
                "wind_direction_10m": [90.0],
            }
        }
        mock_resp.raise_for_status = MagicMock()

        with patch.object(jb._HTTP, "get", return_value=mock_resp):
            with pytest.raises(DataSourceError, match="Open-Meteo returned 1 hours"):
                fetch_weather_history(sample_job)

    def test_fetch_weather_history_network_exception_raises_datasource_error(self, sample_job):
        with patch.object(jb._HTTP, "get", side_effect=requests.RequestException("Connection error")):
            with pytest.raises(DataSourceError, match="Open-Meteo unavailable"):
                fetch_weather_history(sample_job)

    def test_fetch_weather_history_malformed_json_raises_datasource_error(self, sample_job):
        mock_resp = MagicMock()
        mock_resp.json.side_effect = ValueError("Invalid JSON")
        mock_resp.raise_for_status = MagicMock()

        with patch.object(jb._HTTP, "get", return_value=mock_resp):
            with pytest.raises(DataSourceError, match="Open-Meteo unavailable"):
                fetch_weather_history(sample_job)


class TestFetchStaticGrids:
    def test_fetch_static_grids_cache_hit(self, monkeypatch, tmp_path: Path, sample_job):
        monkeypatch.setattr(jb, "STATIC_CACHE_DIR", str(tmp_path))
        cached_data = {"elevation": np.ones((8, 8), dtype=np.float32)}

        with patch("app.backend.src.ai.job_builder.load_static_cache", return_value=cached_data):
            grids = fetch_static_grids(sample_job)
            assert grids == cached_data

    @patch("app.backend.src.ai.job_builder.save_static_cache")
    @patch("app.backend.src.ai.job_builder.process_sentinal2_and_worldcover")
    @patch("app.backend.src.ai.job_builder.resolve_sentinel2_bands")
    @patch("app.backend.src.ai.job_builder.extract_terrain_features")
    @patch("app.backend.src.ai.job_builder.resolve_dem_path")
    def test_fetch_static_grids_single_dem_full_flow(
        self,
        mock_resolve_dem,
        mock_extract_terrain,
        mock_resolve_s2,
        mock_process_s2,
        mock_save_cache,
        sample_job,
    ):
        mock_resolve_dem.return_value = ["/path/dem1.tif"]
        h, w = sample_job["grid_h"], sample_job["grid_w"]

        mock_extract_terrain.return_value = {
            "elevation": np.full((h, w), 200.0, dtype=np.float32),
            "slope": np.full((h, w), 3.0, dtype=np.float32),
            "aspect": np.full((h, w), 90.0, dtype=np.float32),
        }

        mock_s2 = SimpleNamespace(
            b04_path="s3://b04",
            b08_path="s3://b08",
            b11_path="s3://b11",
            scl_path="s3://scl",
        )
        mock_resolve_s2.return_value = mock_s2

        mock_process_s2.return_value = {
            "fuel_load": np.full((h, w), 0.7, dtype=np.float32),
            "dryness": np.full((h, w), 0.4, dtype=np.float32),
            "nonburnable": np.zeros((h, w), dtype=bool),
        }

        grids = fetch_static_grids(sample_job)

        assert "elevation" in grids
        assert "slope" in grids
        assert "aspect_sin" in grids
        assert "aspect_cos" in grids
        assert "fuel_load" in grids
        assert "dryness" in grids
        assert "nonburnable" in grids
        assert np.isclose(grids["aspect_sin"][0, 0], 1.0)
        assert np.isclose(grids["aspect_cos"][0, 0], 0.0, atol=1e-5)
        mock_save_cache.assert_called_once()

    @patch("app.backend.src.ai.job_builder.save_static_cache")
    @patch("app.backend.src.ai.job_builder.process_sentinal2_and_worldcover")
    @patch("app.backend.src.ai.job_builder.resolve_sentinel2_bands")
    @patch("app.backend.src.ai.job_builder.extract_terrain_features")
    @patch("app.backend.src.ai.job_builder.resolve_dem_path")
    def test_fetch_static_grids_multiple_dem_warning_branch(
        self,
        mock_resolve_dem,
        mock_extract_terrain,
        mock_resolve_s2,
        mock_process_s2,
        mock_save_cache,
        sample_job,
    ):
        mock_resolve_dem.return_value = ["/path/dem1.tif", "/path/dem2.tif"]
        h, w = sample_job["grid_h"], sample_job["grid_w"]

        mock_extract_terrain.return_value = {
            "elevation": np.zeros((h, w), dtype=np.float32),
            "slope": np.zeros((h, w), dtype=np.float32),
            "aspect": np.zeros((h, w), dtype=np.float32),
        }

        mock_resolve_s2.return_value = SimpleNamespace(
            b04_path="b4", b08_path="b8", b11_path="b11", scl_path=None
        )
        mock_process_s2.return_value = {
            "fuel_load": np.zeros((h, w), dtype=np.float32),
            "dryness": np.zeros((h, w), dtype=np.float32),
            "nonburnable": np.zeros((h, w), dtype=bool),
        }

        with patch.object(jb.log, "warning") as mock_log_warn:
            grids = fetch_static_grids(sample_job)
            mock_log_warn.assert_called_once()

            format_msg, *args = mock_log_warn.call_args[0]
            rendered_msg = format_msg % tuple(args) if args else format_msg
            assert "bbox spans 2 DEM tiles" in rendered_msg

        assert "elevation" in grids


class TestBuildVolunteerPayload:
    def test_build_volunteer_payload_custom_params(self):
        weather_history = [
            {
                "wind_u": np.array([[1.0, 2.0]]),
                "wind_v": np.array([[3.0, 4.0]]),
                "temperature": np.array([[20.0, 21.0]]),
                "rel_humidity": np.array([[50.0, 55.0]]),
            }
        ]
        static_grids = {
            "elevation": np.array([[100.0, 105.0]]),
            "slope": np.array([[1.0, 1.5]]),
        }
        ignition_mask = np.array([[True, False]])
        custom_params = {"p_continue": 0.8}

        payload = build_volunteer_payload(
            job_id="job-123",
            weather_history=weather_history,
            static_grids=static_grids,
            ignition_mask=ignition_mask,
            cell_size_m=30.0,
            n_steps=10,
            grid_bounds=[18.0, -34.0, 19.0, -33.0],
            containment_lines=["LINESTRING(18.2 -33.5, 18.3 -33.6)"],
            params=custom_params,
        )

        assert payload["job_id"] == "job-123"
        assert payload["cell_size_m"] == 30.0
        assert payload["n_steps"] == 10
        assert payload["params"] == custom_params
        assert isinstance(payload["weather_history"], list)
        assert isinstance(payload["static_grids"]["elevation"], list)
        assert payload["ignition_mask"] == [[True, False]]

    def test_build_volunteer_payload_default_params_fallback(self):
        weather_history = []
        static_grids = {}
        ignition_mask = np.zeros((2, 2), dtype=bool)

        payload = build_volunteer_payload(
            job_id="job-default",
            weather_history=weather_history,
            static_grids=static_grids,
            ignition_mask=ignition_mask,
            cell_size_m=20.0,
            n_steps=5,
            grid_bounds=[0.0, 0.0, 1.0, 1.0],
            containment_lines=[],
            params=None,  # Tests `params or DEFAULT_DCA_PARAMS`
        )

        assert payload["params"] == DEFAULT_DCA_PARAMS