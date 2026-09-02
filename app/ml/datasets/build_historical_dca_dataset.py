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

def build_fire_event_package(
    fire_id: str,
    center_lat: float,
    center_lon: float,
    start_time: datetime,
    duration_hours: int,
    bbox: tuple[float, float, float, float],    # (min_lon, min_lat, max_lon, max_lat)
    target_shape: tuple[int, int],
    pre_fire_bands: dict[str, str], # b04, b08, b11, b12
    post_fire_bands: dict[str, str],    # b08, b12
    dem_path: str,
    output_dir: str = "app/datasets/historical_dca",
    worldcover_path: str | None = None,
    scl_path: str | None = None,
) -> Path: 
    H, W = target_shape
    min_lon, min_lat, max_lon, max_lat = bbox
    
    # 1. ground truth burn scar via dNBR
    print(f"[{fire_id}] Computing dNBR ground truth mask...")
    target_burned_mask = compile_dnbr_mask(
        pre_b08_path=pre_fire_bands["b08"],
        pre_b12_path=pre_fire_bands["b12"],
        post_b08_path=post_fire_bands["b08"],
        post_b12_path=post_fire_bands["b12"],
        target_shape=target_shape,
    )
    
    # 2. static terrain and vegetation features
    print(f"[{fire_id}] Extracting static terrain and fuel features...")
    veg_data = process_sentinal2_and_worldcover(
        worldcover_map_path=worldcover_path,
        scl_path=scl_path,
        b04_path=pre_fire_bands["b04"],
        b08_path=pre_fire_bands["b08"],
        b11_path=pre_fire_bands["b11"],
        min_lon=min_lon,
        min_lat=min_lat,
        max_lat=max_lat,
        target_shape=target_shape,
    )
    
    terrain_data = extract_terrain_features(
        dem_path=dem_path,
        min_lon=min_lon,
        min_lat=min_lat,
        max_lon=max_lon,
        max_lat=max_lat,
        target_shape=target_shape,
    )
    
    aspect_rad = np.radians(terrain_data["aspect"])
    static_grids = {
        "elevation": terrain_data["elevation"].astype(np.float32),
        "slope": terrain_data["slope"].astype(np.float32),
        "aspect_sin": np.sin(aspect_rad).astype(np.float32),
        "aspect_cos": np.cos(aspect_rad).astype(np.float32),
        "fuel_load": veg_data["fuel_load"].astype(np.float32),
        "dryness": veg_data["dryness"].astype(np.float32),
    }
    
    # 3. initial ignition mask (point centered at ignition coordinates)
    ignition_mask = np.zeros((H, W), dtype=bool)

    # map lat/lon to grid row/col
    row = int(np.clip((max_lat - center_lat) / (max_lat - min_lat) * H, 0, H -1))
    col = int(np.clip((center_lon - min_lon) / (max_lon - min_lon) * W, 0, W -1))
    ignition_mask[row, col] = True
    
    # 4. hourly weather timeline
    print(f"[{fire_id}] Fetching historical weather archive...")
    end_time = start_time + timedelta(hours=duration_hours)
    hourly_weather = fetch_historical_hourly_weather(
        lat=center_lat,
        lon=center_lon,
        start_dt=start_time,
        end_dt=end_time,
        target_shape=target_shape,
    )
    
    # 5. pack into .npz
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    file_dest = out_path / f"{fire_id}.npz"
    
    np.savez_compressed(
        file_dest,
        fire_id=fire_id,
        target_burned_mask=target_burned_mask,
        ignition_mask=ignition_mask,
        static_elevation=static_grids["elevation"],
        static_slope=static_grids["slope"],
        static_aspect_sin=static_grids["aspect_sin"],
        static_aspect_cos=static_grids["aspect_cos"],
        static_fuel_load=static_grids["fuel_load"],
        static_dryness=static_grids["dryness"],
        weather_u=np.stack([w["wind_u"] for w in hourly_weather], axis=0),
        weather_v=np.stack([w["wind_v"] for w in hourly_weather], axis=0),
        weather_temp=np.stack([w["temperature"] for w in hourly_weather], axis=0),
        weather_rh=np.stack([w["rel_humidity"] for w in hourly_weather], axis=0),
        duration_hours=duration_hours,
        grid_shape=np.array([H, W]),
    )
    
    print(f"Successfully packed fire event {fire_id} to {file_dest}")
    


