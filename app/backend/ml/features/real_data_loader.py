# imports other classes in this folder
# combines fuel_load, terrain for static data
# and gets current weather

from typing import Optional

import asyncio
import numpy as np

from app.backend.ml.features.fuel_load import process_sentinal2_and_worldcover
from app.backend.ml.features.terrain import extract_terrain_features
from app.backend.ml.features.weather_adapter import fetch_realtime_weather_features


async def load_real_inference_data(
    b04_path: str,
    b08_path: str,
    b11_path: str,
    dem_path: str,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    worldcover_path: Optional[str] = None,
    worldcover_year: int = 2021,
    scl_path: Optional[str] = None,
    target_shape: tuple[int, int] = (64, 64),
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Put static weather feature dictionaries from real datasets to replace synhtetic_dat.py for fire prediction calls"""

    veg_data, terrain_data = await asyncio.gather(
        asyncio.to_thread(
            process_sentinal2_and_worldcover,
            worldcover_map_path=worldcover_path,
            worldcover_year=worldcover_year,
            scl_path=scl_path,
            b04_path=b04_path,
            b08_path=b08_path,
            b11_path=b11_path,
            min_lon=min_lon,
            min_lat=min_lat,
            max_lon=max_lon,
            max_lat=max_lat,
            target_shape=target_shape,
        ),
        asyncio.to_thread(
            extract_terrain_features,
            dem_path=dem_path,
            min_lon=min_lon,
            min_lat=min_lat,
            max_lon=max_lon,
            max_lat=max_lat,
            target_shape=target_shape,
        )
    )

    # comb into unified 'static' feature dict
    static = {
        "elevation": terrain_data["elevation"],
        "slope": terrain_data["slope"],
        "aspect": terrain_data["aspect"],
        "fuel_load": veg_data["fuel_load"],
        "dryness": veg_data["dryness"],
        "valid_mask": veg_data["valid_mask"],
    }

    # real-time weather features for center point
    center_lat = (min_lat + max_lat) / 2.0
    center_lon = (min_lon + max_lon) / 2.0

    weather = await fetch_realtime_weather_features(
        center_lat=center_lat, center_lon=center_lon, target_shape=target_shape
    )

    return static, weather
