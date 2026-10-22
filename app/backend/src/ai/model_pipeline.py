from __future__ import annotations

import torch
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import numpy as np
from pathlib import Path

from app.backend.ml.features.normalization import DeltaNormalizer, RawChannelNormalizer
from app.backend.ml.models.nowcast_model import WeatherDeltaModel, WeatherDeltaModelConfig
from app.backend.src.ai.dca import run_dca
from app.backend.src.ai.sim_constants import TICKS_PER_HOUR

KMH_PER_MS = 3.6

@dataclass
class WeatherForecaster:
    model: WeatherDeltaModel
    raw_norm: RawChannelNormalizer
    delta_norm: DeltaNormalizer
    wind_scale: float #m/s -> model wind units
    max_hours: int
    meta: dict # meatadata.json skills scores, channels, and units

def load_weather_forecaster(model_dir: str | Path, device: str | torch.device) -> WeatherForecaster:
    """Builds the convLSTM exactly as it is trained using metadata.json"""
    model_dir = Path(model_dir)
    meta = json.loads((model_dir / "metadata.json").read_text())
    if meta["input_dim"] != 6:
        raise ValueError(f"Expected 6 input channels(4 weather + hour sin/cos) only got {meta['input_dim']}")

    model = WeatherDeltaModel(WeatherDeltaModelConfig(input_dim=meta["input_dim"]))
    model.load_state_dict(torch.load(model_dir / "model.pt", map_location=device))
    model.to(device).eval()

    raw_norm, delta_norm = RawChannelNormalizer(), DeltaNormalizer()
    raw_norm.load(str(model_dir / "raw_normalizer.json"))
    delta_norm.load(str(model_dir / "delta_normalizer.json"))

    return WeatherForecaster(
        model=model,
        raw_norm=raw_norm,
        delta_norm=delta_norm,
        wind_scale=KMH_PER_MS if meta["units"]["wind_u"] == "km/h" else 1.0,
        max_hours=meta["rollout_steps"],
        meta=meta
    )

def summarize_hourly_weather(hourly_weather: list[dict[str, np.ndarray]]) -> list[dict]:
    """Grid average weather, per hour"""
    summary = []
    for hour, w in enumerate(hourly_weather):
        u,v = float(np.mean(w["wind_u"])), float(np.mean(w["wind_v"]))
        summary.append({
            "hour": hour,
            "temperature_c": round(float(np.mean(w["temperature"])), 1),
            "rel_humidity_pct": round(float(np.mean(w["rel_humidity"])), 1),
            "wind_speed_kmh": round(float(np.hypot(u, v)) * KMH_PER_MS, 1),
            "wind_dir_deg": round(float(np.degrees(np.arctan2(-u, -v)) % 360)),
        })
    return summary

def model_summary(forecaster: WeatherForecaster | None) -> dict | None:
    """Accuracy of the forecast model on held out year for display"""
    if forecaster is None:
        return None
    meta = forecaster.meta
    return {
        "mean_skill": round(meta["mean_skill"], 3),
        "val_years": [f.removeprefix("weather_tensors_").removesuffix(".npz") for f in meta.get("val_files", [])],
        "skill_by_channel": {
            ch: {hour: round(v["skill"], 3) for hour, v in steps.items()}
            for ch, steps in meta["val_metrics"].items()
        }
    }
    
def autoregressive_weather_forecast(
    forecaster: WeatherForecaster,
    init_weather_history: torch.Tensor,
    n_hours_ahead: int,
    last_hour_utc: datetime | None = None,
    device: str | torch.device = "cuda",
) -> list[dict[str, np.ndarray]]:
    """
    Rolls the convLSTM forward to autoregressively predict future hourly weather grids.
    """
    s = forecaster.wind_scale
    hist = init_weather_history.to(device).float().clone()
    hist[:, :, 0:2] *= s
    T_in, H, W = hist.shape[1], hist.shape[-2], hist.shape[-1]

    def stat(arr):
        return torch.tensor(arr, dtype=torch.float32, device=device).view(1, -1, 1, 1)

    raw_mean, raw_std = stat(forecaster.raw_norm.stats.mean), stat(forecaster.raw_norm.stats.std)
    d_mean, d_std = stat(forecaster.delta_norm.stats.mean), stat(forecaster.delta_norm.stats.std)
    lo = stat([-20.0 * s, -20.0 * s, 0.0, 0.0])
    hi = stat([20.0 * s, 20.0 * s, 48.0, 100.0])

    if last_hour_utc is None:
        last_hour_utc = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

    def normalized_frame(weather: torch.Tensor, ts: datetime) -> torch.Tensor:
        """weather [1,4,H,W] in model units -> normalised [1,6,H,W]"""
        angle = 2 * np.pi * (ts.hour + ts.minute / 60.0) / 24.0
        hs = torch.full((1, 1, H, W), float(np.sin(angle)), device=device)
        hc = torch.full((1, 1, H, W), float(np.cos(angle)), device=device)
        return (torch.cat([weather, hs, hc], dim=1) - raw_mean) / raw_std

    def to_dca(weather: torch.Tensor) -> dict[str, np.ndarray]:
        f = weather.squeeze(0).cpu().numpy()
        return {
            "wind_u": f[0] / s,
            "wind_v": f[1] / s,
            "temperature": f[2],
            "rel_humidity": f[3],
        }

    window = torch.stack(
        [normalized_frame(hist[:, i], last_hour_utc - timedelta(hours=T_in - 1 - i)) for i in range(T_in)],
        dim=1,
    )
    current = hist[:, -1]
    forecasted_weather = [to_dca(current)]

    with torch.no_grad():
        for step in range(1, min(n_hours_ahead, forecaster.max_hours) + 1):
            delta = forecaster.model(window) * d_std + d_mean
            current = torch.clamp(current + delta, lo, hi)
            forecasted_weather.append(to_dca(current))
            next_frame = normalized_frame(current, last_hour_utc + timedelta(hours=step))
            window = torch.cat([window[:, 1:], next_frame.unsqueeze(1)], dim=1)

    return forecasted_weather

def run_convlstm_dca(
    forecaster: WeatherForecaster | None,
    weather_history: torch.Tensor,
    static_grids: dict[str, np.ndarray],
    cell_size_m: float,
    n_steps: int = 4,
    ignition_mask: np.ndarray | None = None,
    containment_lines: list[str] | None = None,
    grid_bounds: tuple[float, float, float, float] | None = None,
    params: dict | None = None,
) -> tuple[list[np.ndarray], list[dict[str, np.ndarray]]]:
    """
    Combines the two models for the spread simulation and returns burn history and weather grids per hour
    """

    device = "cuda" if torch.cuda.is_available() else "cpu"

    n_hours = max(1, int(np.ceil(n_steps / TICKS_PER_HOUR))) 

    # run lstm to predict weather
    if forecaster is None:
        last = weather_history[0, -1].cpu().numpy()
        hourly_weather = [{"wind_u": last[0], "wind_v": last[1], "temperature": last[2], "rel_humidity": last[3]}]
    else:
        hourly_weather = autoregressive_weather_forecast(
            forecaster=forecaster,
            init_weather_history=weather_history,
            n_hours_ahead=n_hours,
            device=device,
        )

    history = run_dca(
        weather_grids=hourly_weather,
        static_grids=static_grids,
        cell_size_m=cell_size_m,
        n_steps=n_steps,
        ignition_mask=ignition_mask,
        containment_lines=containment_lines,
        grid_bounds=grid_bounds,
        params=params,
    )

    return history, hourly_weather
