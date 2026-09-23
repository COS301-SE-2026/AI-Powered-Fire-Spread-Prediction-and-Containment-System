# Real-time, per-bearing terrain bias for live-map fire growth animation
# Handles slope + aspect and land-cover

from __future__ import annotations

import base64
import math
import zlib
from collections import OrderedDict

import numpy as np

from app.backend.ml.features.terrain import extract_terrain_features
from app.backend.ml.features.fuel_load import _read_worldcover_window, load_fuel_base_weights
from app.backend.src.services.cache import cache_client

METERS_PER_DEG_LAT = 111_320.0

N_BEARINGS = 16
SAMPLE_RADIUS_KM = 1.0
GRID_SHAPE = (48, 48)
BBOX_PAD_KM = max(SAMPLE_RADIUS_KM * 3.0, 1.5)

MAX_L1_ENTRIES = 500
L1_CACHE: "OrderedDict[tuple[float, float], dict]" = OrderedDict()
L2_TTL_SECONDS = 30 * 24 * 3600 # 30 days

def cache_key(lat: float, lng: float) -> tuple[float, float]:
    return (round(lat, 2), round(lng, 2))   # ~1km buckets

def redis_key(lat: float, lng: float) -> str:
    key_lat, key_lng = cache_key(lat, lng)
    return f"terrain:bias_grids:{key_lat}:{key_lng}"

def pack_grid(arr: np.array, dtype, type: type) -> str:
    compressed = zlib.compress(arr.astype(dtype).tobytes(), level=6)
    return base64.b64encode(compressed).decode("ascii")

def unpack_grid(raw: str, dtype: type, shape: tuple[int, int]) -> np.array:
    compressed = base64.b64decode(raw)
    return np.frombuffer(zlib.decompress(compressed), dtype=dtype).reshape(shape)

def read_from_12(lat: float, lng: float) -> dict | None:
    if cache_client is None:
        return None
    try:
        data = cache_client.hgetall(redis_key(lat, lng))    
        if not data:
            return None
        
        min_lon, min_lat, max_lon, max_lat = (float(x) for x in data["bounds"].split(","))
        return {
            "bounds": (min_lon, min_lat, max_lon, max_lat),
            "slope": unpack_grid(data["slope"], np.float32, GRID_SHAPE),
            "aspect": unpack_grid(data["aspect"], np.float32, GRID_SHAPE),
            "landcover": unpack_grid(data["landcover"], np.int16, GRID_SHAPE),
        }
    except Exception:
        return None
    
def write_to_12(lat: float, lng: float, entry: dict) -> None:
    if cache_client is None:
        return
    try:
        min_lon, min_lat, max_lon, max_lat = entry["bounds"]
        cache_client.hset(
            redis_key(lat, lng),
            mapping={
                "bounds": f"{min_lon}, {min_lat}, {max_lon}, {max_lat}",
                "slope": pack_grid(entry["slope"], np.float32),
                "aspect": pack_grid(entry["aspect"], np.float32),
                "landcover": pack_grid(entry["landcover"], np.int16),
            },
        )
        cache_client.expire(redis_key(lat, lng), L2_TTL_SECONDS)
    except Exception:
        pass
    

    
