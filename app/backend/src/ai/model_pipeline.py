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
        device: str | torch.device = "cuda"
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
    curr_history = init_weather_history.to(device) # [1, T_in, 4, H, W] | (wind_u, wind_v, rel_humidity, temperature)
    static_feat = static_tensor.to(device) # [1, 6, H, W] | (elevation, slope, aspect_sin, fuel_load, dryness)

    H, W = curr_history.shape[-2:]
    T_in = curr_history.shape[1]

    forecasted_weather = list[dict[str, np.ndarray]] = []

    # store weather hour 0
    base = curr_history[:, -1].squeeze(0).detach.cpu().numpy() 
    forecasted_weather.append({
        "wind_u": base[0],
        "wind_v": base[1],
        "rel_humidity": base[2],
        "temperature": base[3]
    })

    with torch.no_grad():
        for _ in range(n_hours_ahead):

            # tile static terrain across time 
            static_sequence = static_feat.unsqueeze(1).repeat(1, curr_history.shape[1], 1, 1, 1)

            # concatenate the weather and the static features
            model_input = torch.cat([curr_history, static_sequence], dim=2)

            # precit the delta for the next hour
            delta = model(model_input)

            # most recent hour + delta
            next_weather = curr_history[:, 1] + delta

            # append hourly output
            frame = next_weather.squeeze(0).detach().cpu().numpy()
            forecasted_weather.append({
                "wind_u": frame[0],
                "wind_v": frame[1],
                "rel_humidity": np.clip(frame[2], 0.0, 1.0),
                "temperature": frame[3]
            })
            #drop oldest frame and append predicted frame 
            curr_history = torch.cat([curr_history[:,1:], next_weather.unsqueeze(1)], dim=1)

    return forecasted_weather
