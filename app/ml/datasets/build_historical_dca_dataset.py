from __future__ import annotations

import argparse
from datetime import datetime, timedelta

import math
from pathlib import Path

import httpx
import numpy as np
import rasterio
from rasterio.enums import Resampling

from ml.features.fuel_load import process_sentinal2_and_worldcover
from ml.features.terrain import extract_terrain_features

METERS_PER_DEG_LAT = 111_320.0

def compute_dnbr_mask(
    pre_b08_path: str,
    pre_b12_path: str,
    post_b08_path: str,
    post_b12_path: str,
    target_shape: tuple[int, int],
    dnbr_threshold: float = 0.27, # standard USGS moderate-to-high burn severity threshold
) -> np.ndarray:
    """Computes differenced Normalised Burn Ratio (dNBR) and returns a binary burned mask"""
    H, W = target_shape
    
    def read_and_resample(path: str) -> np.ndarray:
        with rasterio.open(path) as src:
            return src.read(
                1,
                out_shape=(H,W),
                resampling=Resampling.bilinear,
            ).astype(np.float32)
            
    pre_nir = read_and_resample(pre_b08_path)
    pre_swir = read_and_resample(pre_b12_path)
    post_nir = read_and_resample(post_b08_path)
    post_swir = read_and_resample(post_b12_path)
    
    eps = 1e-6
    pre_nbr = (pre_nir - pre_swir) / (pre_nir + pre_swir + eps)
    post_nbr = (post_nir - post_swir) / (post_nir + post_swir + eps)
    
    dnbr = pre_nbr - post_nbr
    # burned pixels exceeded threshold and exclude non-vegetated anomalies
    burned_mask = (dnbr >= dnbr_threshold) & np.isfinite(dnbr)
    return burned_mask

def fetch_historical_hourly_weather(
    lat: float,
    lon: float,
    start_dt: datetime,
    end_dt: datetime,
    target_shape: tuple[int, int],
) -> list[dict[str, np.ndarray]]:
    """Fetches exact historical hourly weather from Open-Meteo Archive API"""
    H, W = target_shape
    start_str = start_dt.strftime("%Y-%m-%d")
    end_str = end_dt.strftime("%Y-%m-%d")
    
    url = (
        "https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&"
        f"start_date={start_str}&end_date={end_str}&"
        "hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"
    )
    
    with httpx.Client(timeout=15.0) as client:
        resp = client.get(url)
        resp.raise_for_status()
        data = resp.json()["hourly"]
        
    hourly_records = []
    n_hours = len(data["time"])
    
    for i in range(n_hours):
        t_c = float(data["temperature_2m"][i])
        rh = float(data["relative_humidity"][i]) / 100.0
        ws = float(data["wind_speed_10m"][i]) / 3.6     # km/h to m/s
        wd = math.radians(float(data["wind_direction_10m"][i]))
        
        u_val = float(-ws * math.sin(wd))
        v_val = float(-ws * math.cos(wd))
        
        hourly_records.append({
            "wind_u": np.full((H, W), u_val, dtype=np.float32),
            "wind_v": np.full((H, W), v_val, dtype=np.float32),
            "temperature": np.full((H, W), t_c, dtype=np.float32),
            "rel_humidity": np.full((H, W), np.clip(rh, 0.0, 1.0), dtype=np.float32),
        })
        
    return hourly_records


