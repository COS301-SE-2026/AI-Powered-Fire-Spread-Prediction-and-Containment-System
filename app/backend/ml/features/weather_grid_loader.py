from __future__ import annotations

import numpy as np
import pandas as pd

DYNAMIC_CHANNELS = ["wind_u", "wind_v", "temperature", "relative_humidity"]

SA_LAT_MIN, SA_LAT_MAX = -35.0, -22.0
SA_LON_MIN, SA_LON_MAX = 16.0, 33.0


def build_sa_grid_shape(resolution_deg: float = 0.5) -> tuple[int, int]:
    lats = np.arange(SA_LAT_MAX, SA_LAT_MIN - resolution_deg, -resolution_deg)
    lons = np.arange(SA_LON_MIN, SA_LON_MAX + resolution_deg, resolution_deg)
    return len(lats), len(lons)


def load_weather_grid_csv(
    csv_path: str, resolution_deg: float = 0.5
) -> tuple[np.ndarray, list[str]]:

    df = pd.read_csv(csv_path)
    df = df.rename(columns={"latitude": "lat", "longitude": "lon"})
    H, W = build_sa_grid_shape(resolution_deg)
    lats = np.sort(df["lat"].unique())[::-1]  # descending order, north to south
    lons = np.sort(df["lon"].unique())

    if len(lats) != H or len(lons) != W:
        raise ValueError(
            f"{csv_path}: found {len(lats)}x{len(lons)} distinct coords, "
            f"expected {H}x{W} — fetch may be incomplete for this year."
        )

    lat_index = {lat: i for i, lat in enumerate(lats)}
    lon_index = {lon: i for i, lon in enumerate(lons)}

    timestamps = sorted(df["datetime"].unique())
    time_index = {ts: i for i, ts in enumerate(timestamps)}
    T = len(timestamps)

    tensor = np.full((T, 4, H, W), np.nan, dtype=np.float32)
    t_idx = df["datetime"].map(time_index).to_numpy()
    row_idx = df["lat"].map(lat_index).to_numpy()
    col_idx = df["lon"].map(lon_index).to_numpy()

    for c, channel in enumerate(DYNAMIC_CHANNELS):
        tensor[t_idx, c, row_idx, col_idx] = df[channel].to_numpy(dtype=np.float32)

    if np.isnan(tensor).any():
        n_missing = np.isnan(tensor).sum()
        raise ValueError(
            f"{csv_path}: {n_missing} missing (time, channel, lat, lon) cells "
            "after pivot — likely a partial fetch."
        )
    return tensor, timestamps