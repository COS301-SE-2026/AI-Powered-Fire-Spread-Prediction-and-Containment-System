from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pytest
import torch

from app.backend.ml.models.nowcast_model import (
    WeatherDeltaModel,
    WeatherDeltaModelConfig,
)
from app.backend.src.ai.model_pipeline import (
    KMH_PER_MS,
    WeatherForecaster,
    autoregressive_weather_forecast,
    load_weather_forecaster,
    model_summary,
    run_convlstm_dca,
    summarize_hourly_weather,
)
from app.backend.src.ai.schema import BURNED, BURNING, UNBURNED


@pytest.fixture(scope="module")
def synthetic_model_dir(tmp_path_factory) -> Path:
    """Creates a real disk directory with genuine weights and normalizer files."""
    model_dir = tmp_path_factory.mktemp("weather_model_bundle")
    input_dim = 6
    rollout_steps = 3

    meta_payload = {
        "input_dim": input_dim,
        "rollout_steps": rollout_steps,
        "mean_skill": 0.842,
        "units": {"wind_u": "km/h"},
        "val_files": [
            "weather_tensors_2021.npz",
            "weather_tensors_2022.npz",
        ],
        "val_metrics": {
            "wind_u": {"1": {"skill": 0.812}, "2": {"skill": 0.795}},
            "temperature": {"1": {"skill": 0.884}, "2": {"skill": 0.861}},
        },
    }
    (model_dir / "metadata.json").write_text(json.dumps(meta_payload))

    config = WeatherDeltaModelConfig(input_dim=input_dim)
    real_model = WeatherDeltaModel(config)
    torch.save(real_model.state_dict(), model_dir / "model.pt")

    raw_norm_payload = {
        "mean": [0.0, 0.0, 22.0, 45.0, 0.0, 0.0],
        "std": [5.0, 5.0, 10.0, 20.0, 1.0, 1.0],
    }
    delta_norm_payload = {
        "mean": [0.0, 0.0, 0.0, 0.0],
        "std": [1.0, 1.0, 2.0, 5.0],
    }
    (model_dir / "raw_normalizer.json").write_text(json.dumps(raw_norm_payload))
    (model_dir / "delta_normalizer.json").write_text(json.dumps(delta_norm_payload))

    return model_dir


@pytest.fixture
def base_static_grids():
    """Builds synthetic geospatial terrain grids matching DCA expectations."""
    h, w = 12, 12
    return {
        "elevation": np.full((h, w), 300.0, dtype=np.float32),
        "slope": np.full((h, w), 2.0, dtype=np.float32),
        "aspect_sin": np.zeros((h, w), dtype=np.float32),
        "aspect_cos": np.ones((h, w), dtype=np.float32),
        "fuel_load": np.full((h, w), 0.75, dtype=np.float32),
        "dryness": np.full((h, w), 0.65, dtype=np.float32),
        "nonburnable": np.zeros((h, w), dtype=bool),
    }


class TestModelPipelineIntegration:
    def test_load_weather_forecaster_from_disk(self, synthetic_model_dir: Path):
        forecaster = load_weather_forecaster(synthetic_model_dir, device="cpu")

        assert isinstance(forecaster, WeatherForecaster)
        assert isinstance(forecaster.model, torch.nn.Module)
        assert forecaster.model.training is False
        assert forecaster.wind_scale == KMH_PER_MS
        assert forecaster.max_hours == 3
        assert forecaster.meta["mean_skill"] == 0.842

    def test_model_summary_integration(self, synthetic_model_dir: Path):
        forecaster = load_weather_forecaster(synthetic_model_dir, device="cpu")
        summary = model_summary(forecaster)

        assert summary is not None
        assert summary["mean_skill"] == 0.842
        assert summary["val_years"] == ["2021", "2022"]
        assert "wind_u" in summary["skill_by_channel"]
        assert summary["skill_by_channel"]["wind_u"]["1"] == 0.812

    def test_autoregressive_forecast_and_weather_summary_integration(
        self, synthetic_model_dir: Path
    ):
        forecaster = load_weather_forecaster(synthetic_model_dir, device="cpu")
        batch, time_steps, channels, h, w = 1, 3, 4, 12, 12
        weather_history = torch.ones((batch, time_steps, channels, h, w), dtype=torch.float32)

        start_time = datetime(2026, 10, 27, 8, 0, tzinfo=timezone.utc)
        forecast_grids = autoregressive_weather_forecast(
            forecaster=forecaster,
            init_weather_history=weather_history,
            n_hours_ahead=2,
            last_hour_utc=start_time,
            device="cpu",
        )

        assert len(forecast_grids) == 3
        for frame in forecast_grids:
            assert set(frame.keys()) == {"wind_u", "wind_v", "temperature", "rel_humidity"}
            assert frame["wind_u"].shape == (h, w)
            assert not np.isnan(frame["wind_u"]).any()
            assert not np.isnan(frame["temperature"]).any()

        hourly_summary = summarize_hourly_weather(forecast_grids)
        assert len(hourly_summary) == 3
        for idx, hr_data in enumerate(hourly_summary):
            assert hr_data["hour"] == idx
            assert isinstance(hr_data["temperature_c"], float)
            assert isinstance(hr_data["rel_humidity_pct"], float)
            assert isinstance(hr_data["wind_speed_kmh"], float)
            assert 0 <= hr_data["wind_dir_deg"] < 360

    def test_run_convlstm_dca_full_system_integration(
        self, synthetic_model_dir: Path, base_static_grids
    ):
        forecaster = load_weather_forecaster(synthetic_model_dir, device="cpu")
        h, w = 12, 12
        weather_history = torch.ones((1, 2, 4, h, w), dtype=torch.float32)

        ignition_mask = np.zeros((h, w), dtype=bool)
        ignition_mask[6, 6] = True

        containment_lines = ["LINESTRING(18.401 -33.901, 18.405 -33.901)"]
        grid_bounds = (18.40, -33.95, 18.45, -33.90)

        history, hourly_weather = run_convlstm_dca(
            forecaster=forecaster,
            weather_history=weather_history,
            static_grids=base_static_grids,
            cell_size_m=30.0,
            n_steps=4,
            ignition_mask=ignition_mask,
            containment_lines=containment_lines,
            grid_bounds=grid_bounds,
        )

        assert len(history) == 5
        assert len(hourly_weather) >= 1

        for grid in history:
            assert isinstance(grid, np.ndarray)
            assert grid.shape == (h, w)
            assert np.all(np.isin(grid, [UNBURNED, BURNING, BURNED]))

        assert history[0][6, 6] == BURNING or history[-1][6, 6] in (BURNING, BURNED)

    def test_run_convlstm_dca_fallback_without_forecaster(self, base_static_grids):
        h, w = 12, 12
        weather_history = torch.full((1, 2, 4, h, w), 2.0, dtype=torch.float32)

        ignition_mask = np.zeros((h, w), dtype=bool)
        ignition_mask[5, 5] = True

        history, hourly_weather = run_convlstm_dca(
            forecaster=None,
            weather_history=weather_history,
            static_grids=base_static_grids,
            cell_size_m=30.0,
            n_steps=2,
            ignition_mask=ignition_mask,
        )

        assert len(history) == 3
        assert len(hourly_weather) == 1
        assert hourly_weather[0]["wind_u"].shape == (h, w)
        assert np.allclose(hourly_weather[0]["wind_u"], 2.0)