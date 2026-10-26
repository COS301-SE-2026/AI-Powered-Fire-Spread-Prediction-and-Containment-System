import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import torch

from app.backend.src.ai.model_pipeline import (
    KMH_PER_MS,
    WeatherForecaster,
    autoregressive_weather_forecast,
    load_weather_forecaster,
    model_summary,
    run_convlstm_dca,
    summarize_hourly_weather,
)


@pytest.fixture
def sample_metadata():
    return {
        "input_dim": 6,
        "rollout_steps": 4,
        "mean_skill": 0.8123,
        "val_files": ["weather_tensors_2022.npz", "weather_tensors_2023.npz"],
        "val_metrics": {
            "temp": {"1": {"skill": 0.8543}},
            "rh": {"1": {"skill": 0.7891}},
        },
        "units": {"wind_u": "km/h"},
    }


@pytest.fixture
def dummy_forecaster(sample_metadata):
    mock_model = MagicMock()
    mock_model.return_value = torch.zeros((1, 4, 4, 4), dtype=torch.float32)

    raw_norm = MagicMock()
    raw_norm.stats.mean = np.zeros(6, dtype=np.float32)
    raw_norm.stats.std = np.ones(6, dtype=np.float32)

    delta_norm = MagicMock()
    delta_norm.stats.mean = np.zeros(4, dtype=np.float32)
    delta_norm.stats.std = np.ones(4, dtype=np.float32)

    return WeatherForecaster(
        model=mock_model,
        raw_norm=raw_norm,
        delta_norm=delta_norm,
        wind_scale=KMH_PER_MS,
        max_hours=4,
        meta=sample_metadata,
    )


class TestLoadWeatherForecaster:
    def test_load_weather_forecaster_success(self, tmp_path, sample_metadata):
        meta_file = tmp_path / "metadata.json"
        meta_file.write_text(json.dumps(sample_metadata))

        model_file = tmp_path / "model.pt"
        torch.save({}, model_file)

        raw_norm_file = tmp_path / "raw_normalizer.json"
        raw_norm_file.write_text("{}")

        delta_norm_file = tmp_path / "delta_normalizer.json"
        delta_norm_file.write_text("{}")

        with patch("app.backend.src.ai.model_pipeline.WeatherDeltaModel") as mock_model_cls, patch(
            "app.backend.src.ai.model_pipeline.RawChannelNormalizer"
        ) as mock_raw_cls, patch(
            "app.backend.src.ai.model_pipeline.DeltaNormalizer"
        ) as mock_delta_cls, patch(
            "torch.load", return_value={}
        ):
            mock_model_instance = MagicMock()
            mock_model_cls.return_value = mock_model_instance
            mock_model_instance.to.return_value = mock_model_instance

            forecaster = load_weather_forecaster(tmp_path, device="cpu")

            assert forecaster.wind_scale == KMH_PER_MS
            assert forecaster.max_hours == 4
            assert forecaster.meta["input_dim"] == 6

    def test_load_weather_forecaster_wind_unit_ms(self, tmp_path, sample_metadata):
        sample_metadata["units"]["wind_u"] = "m/s"
        (tmp_path / "metadata.json").write_text(json.dumps(sample_metadata))
        (tmp_path / "model.pt").touch()

        with patch("app.backend.src.ai.model_pipeline.WeatherDeltaModel") as mock_model_cls, patch(
            "app.backend.src.ai.model_pipeline.RawChannelNormalizer"
        ), patch("app.backend.src.ai.model_pipeline.DeltaNormalizer"), patch(
            "torch.load", return_value={}
        ):
            mock_model_instance = MagicMock()
            mock_model_cls.return_value = mock_model_instance
            mock_model_instance.to.return_value = mock_model_instance

            forecaster = load_weather_forecaster(tmp_path, device="cpu")
            assert forecaster.wind_scale == 1.0

    def test_load_weather_forecaster_invalid_channels_raises(self, tmp_path, sample_metadata):
        sample_metadata["input_dim"] = 4
        (tmp_path / "metadata.json").write_text(json.dumps(sample_metadata))

        with pytest.raises(ValueError, match="Expected 6 input channels"):
            load_weather_forecaster(tmp_path, device="cpu")


class TestSummaries:
    def test_summarize_hourly_weather(self):
        hourly_data = [
            {
                "wind_u": np.full((3, 3), 2.0, dtype=np.float32),
                "wind_v": np.full((3, 3), 2.0, dtype=np.float32),
                "temperature": np.full((3, 3), 24.5, dtype=np.float32),
                "rel_humidity": np.full((3, 3), 55.4, dtype=np.float32),
            }
        ]
        summary = summarize_hourly_weather(hourly_data)

        assert len(summary) == 1
        assert summary[0]["hour"] == 0
        assert summary[0]["temperature_c"] == 24.5
        assert summary[0]["rel_humidity_pct"] == 55.4
        assert "wind_speed_kmh" in summary[0]
        assert "wind_dir_deg" in summary[0]

    def test_model_summary(self, dummy_forecaster):
        res = model_summary(dummy_forecaster)
        assert res is not None
        assert res["mean_skill"] == 0.812
        assert res["val_years"] == ["2022", "2023"]
        assert "temp" in res["skill_by_channel"]

    def test_model_summary_none(self):
        assert model_summary(None) is None


class TestAutoregressiveForecast:
    def test_autoregressive_weather_forecast_execution(self, dummy_forecaster):
        # Shape: [B=1, T=3, C=4, H=4, W=4]
        history = torch.zeros((1, 3, 4, 4, 4), dtype=torch.float32)
        n_hours = 2
        ts = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)

        forecasts = autoregressive_weather_forecast(
            forecaster=dummy_forecaster,
            init_weather_history=history,
            n_hours_ahead=n_hours,
            last_hour_utc=ts,
            device="cpu",
        )

        # Returns initial frame + 2 rolled frames
        assert len(forecasts) == 3
        for item in forecasts:
            assert "wind_u" in item
            assert "wind_v" in item
            assert "temperature" in item
            assert "rel_humidity" in item

    def test_autoregressive_weather_forecast_default_timestamp(self, dummy_forecaster):
        history = torch.zeros((1, 2, 4, 4, 4), dtype=torch.float32)
        forecasts = autoregressive_weather_forecast(
            forecaster=dummy_forecaster,
            init_weather_history=history,
            n_hours_ahead=1,
            last_hour_utc=None,
            device="cpu",
        )
        assert len(forecasts) == 2


class TestRunConvlstmDca:
    @patch("app.backend.src.ai.model_pipeline.run_dca")
    def test_run_convlstm_dca_without_forecaster(self, mock_dca):
        mock_dca.return_value = [np.zeros((5, 5), dtype=np.int64)]
        history_tensor = torch.zeros((1, 2, 4, 5, 5), dtype=torch.float32)
        static_grids = {"elevation": np.zeros((5, 5), dtype=np.float32)}

        burn_hist, hourly_weather = run_convlstm_dca(
            forecaster=None,
            weather_history=history_tensor,
            static_grids=static_grids,
            cell_size_m=30.0,
            n_steps=4,
        )

        assert len(burn_hist) == 1
        assert len(hourly_weather) == 1
        mock_dca.assert_called_once()

    @patch("app.backend.src.ai.model_pipeline.run_dca")
    @patch("app.backend.src.ai.model_pipeline.autoregressive_weather_forecast")
    def test_run_convlstm_dca_with_forecaster(self, mock_forecast, mock_dca, dummy_forecaster):
        mock_dca.return_value = [np.zeros((5, 5), dtype=np.int64)]
        mock_forecast.return_value = [
            {"wind_u": 0.0, "wind_v": 0.0, "temperature": 20.0, "rel_humidity": 50.0}
        ]
        history_tensor = torch.zeros((1, 2, 4, 5, 5), dtype=torch.float32)
        static_grids = {"elevation": np.zeros((5, 5), dtype=np.float32)}

        burn_hist, hourly_weather = run_convlstm_dca(
            forecaster=dummy_forecaster,
            weather_history=history_tensor,
            static_grids=static_grids,
            cell_size_m=30.0,
            n_steps=8,
        )

        assert len(burn_hist) == 1
        mock_forecast.assert_called_once()
        mock_dca.assert_called_once()