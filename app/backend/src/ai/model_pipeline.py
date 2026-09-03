from __future__ import annotations

import torch
import numpy as np

from app.ml.models.nowcast_model import WeatherDeltaModel
from app.backend.src.ai.dca import run_dca


def autoregressive_weather_forecast(
    model: WeatherDeltaModel,
    init_weather_history: torch.Tensor,
    static_tensor: torch.Tensor,
    n_hours_ahead: int,
    device: str | torch.device = "cuda",
) -> list[dict[str, np.ndarray]]:
    """
    Rolls the convLSTM forward to autoregressively predict future hourly weather grids.

    Args:
        model => Trained Weather Delta Model
        init_weather_history => Tensor shaped [1, T_in, 4, H, W] | (wind_u, wind_v, rel_humidity, temperature)
        static_tensor => Static terrain raster tensor [1, 6, H, W] | (elevation, slope, aspect_sin, fuel_load, dryness)
        n_hours_ahead => Total hours of the weather forecast

    Return:
        hourly_weather_grids => List of weather dicts for the dca
    """

    model.eval()
    curr_history = init_weather_history.to(
        device
    )  # [1, T_in, 4, H, W] | (wind_u, wind_v, rel_humidity, temperature)
    static_feat = static_tensor.to(
        device
    )  # [1, 6, H, W] | (elevation, slope, aspect_sin, fuel_load, dryness)

    H, W = curr_history.shape[-2:]
    T_in = curr_history.shape[1]

    forecasted_weather: list[dict[str, np.ndarray]] = []

    # store weather hour 0
    base = curr_history[:, -1].squeeze(0).detach().cpu().numpy()
    forecasted_weather.append(
        {
            "wind_u": base[0],
            "wind_v": base[1],
            "rel_humidity": base[2],
            "temperature": base[3],
        }
    )

    with torch.no_grad():
        for _ in range(n_hours_ahead):

            # tile static terrain across time
            static_sequence = static_feat.unsqueeze(1).repeat(
                1, curr_history.shape[1], 1, 1, 1
            )

            # concatenate the weather and the static features
            model_input = torch.cat([curr_history, static_sequence], dim=2)

            # precit the delta for the next hour
            delta = model(model_input)

            # most recent hour + delta
            next_weather = curr_history[:, -1] + delta

            # append hourly output
            frame = next_weather.squeeze(0).detach().cpu().numpy()

            wind_u_clamped = np.clip(frame[0], -20.0, 20.0)  # max 72km/h wind vectors
            wind_v_clamped = np.clip(frame[1], -20, 20)
            rel_humidity_clamped = np.clip(frame[2], 0.0, 1.0)  # 5% to 95% humidity
            temperature_clamped = np.clip(
                frame[3], 0.0, 48.0
            )  # 0 degrees to 48 degrees

            forecasted_weather.append(
                {
                    "wind_u": wind_u_clamped,
                    "wind_v": wind_v_clamped,
                    "rel_humidity": rel_humidity_clamped,
                    "temperature": temperature_clamped,
                }
            )

            clamped_frame = np.stack(
                [
                    wind_u_clamped,
                    wind_v_clamped,
                    rel_humidity_clamped,
                    temperature_clamped,
                ],
                axis=0,
            ).astype(np.float32)

            clamped_tensor = (
                torch.from_numpy(clamped_frame).unsqueeze(0).unsqueeze(1).to(device)
            )

            # drop oldest frame and append predicted frame
            curr_history = torch.cat([curr_history[:, 1:], clamped_tensor], dim=1)

    return forecasted_weather


def run_convlstm_dca(
    convlstm_model: WeatherDeltaModel,
    weather_history: torch.Tensor,
    static_grids: dict[str, np.ndarray],
    cell_size_m: float,
    n_steps: int = 4,
    ignition_mask: np.ndarray | None = None,
    containment_lines: list[str] | None = None,
    grid_bounds: tuple[float, float, float, float] | None = None,
    params: dict | None = None,
) -> list[np.ndarray]:
    """
    Combines the two models for the spread simulation
    """

    device = "cuda" if torch.cuda.is_available() else "cpu"

    n_hours = max(1, int(np.ceil(n_steps / 4)))  # 4 ticks per hour

    # pack the terrain rasters into the correct format [1, 6, H, W]
    static_stack = np.stack(
        [
            static_grids["elevation"],
            static_grids["slope"],
            static_grids["aspect_sin"],
            static_grids["aspect_cos"],
            static_grids["fuel_load"],
            static_grids["dryness"],
        ],
        axis=0,
    ).astype(np.float32)

    static_tensor = torch.from_numpy(static_stack).unsqueeze(0).to(device)

    # run lstm to predict weather
    hourly_weather = autoregressive_weather_forecast(
        model=convlstm_model,
        init_weather_history=weather_history,
        static_tensor=static_tensor,
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

    return history
