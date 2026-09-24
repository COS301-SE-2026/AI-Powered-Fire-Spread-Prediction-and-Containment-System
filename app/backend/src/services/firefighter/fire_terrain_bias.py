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

def read_from_l2(lat: float, lng: float) -> dict | None:
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
    
def write_to_l2(lat: float, lng: float, entry: dict) -> None:
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
    
def dem_vsis3_path(min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> str:
    """
    Copernicus DEM GLO-30 tile path for bbox streamed from public S3 bucket.
    Duplicated from build_training_manifest.py deliberately.
    """
    center_lat = (min_lat + max_lat) / 2.0
    center_lon = (min_lon + max_lon) / 2.0
    title_lat = math.floor(center_lat)
    title_lon = math.floor(center_lon)
    ns = "N" if title_lat >= 0 else "S"
    ew = "E" if title_lon >= 0 else "W"
    lat_str = f"{ns}{abs(title_lat):02d}_00"
    lon_str = f"{ew}{abs(title_lon):03d}_00"
    title_name = f"Copernicus_DSM_COG_10_{lat_str}_{lon_str}_DEM"
    return f"/vsis3/copernicus-dem-30m/{title_name}/{title_name}.tif"

def bbox_for(lat: float, lng: float, pad_km: float) -> tuple[float, float, float, float]:
    dlat = pad_km / (METERS_PER_DEG_LAT / 1000.0)
    dlon = pad_km / ((METERS_PER_DEG_LAT / 1000.0) * math.cos(math.radians(lat)))
    return (lng - dlon, lat - dlat, lng + dlon, lat + dlat)

def fetch_terrain_grids(lat: float, lng: float) -> dict:
    """
    Elevation/slope/aspect (DEM) + landcover class (WorldCover) for small patch
    around fire
    """
    key = cache_key(lat, lng)
    if key in L1_CACHE:
        L1_CACHE.move_to_end(key)
        return L1_CACHE[key]
    
    l2_hit = read_from_l2(lat, lng)
    if l2_hit is not None:
        l1_store(key, l2_hit)
        return l2_hit
    
    min_lon, min_lat, max_lon, max_lat = bbox_for(lat, lng, BBOX_PAD_KM)
    
    terrain = extract_terrain_features(
        dem_path=dem_vsis3_path(min_lon, min_lat, max_lon, max_lat),
        min_lon=min_lon,
        min_lat=min_lat,
        max_lon=max_lon,
        max_lat=max_lat,
        target_shape=GRID_SHAPE,
    )
    landcover = _read_worldcover_window(
        worldcover_map_path=None,
        min_lon=min_lon,
        min_lat=min_lat,
        max_lon=max_lon,
        max_lat=max_lat,
        out_shape=GRID_SHAPE,
    )
    
    entry = {
        "bounds": (min_lon, min_lat, max_lon, max_lat),
        "slope": terrain["slope"],
        "aspect": terrain["aspect"],
        "landcover": landcover,
    }
    
    l1_store(key, entry)
    write_to_l2(lat, lng, entry)
    return entry
    
def l1_store(key: tuple[float, float], entry: dict) -> None:
    L1_CACHE[key] = entry
    L1_CACHE.move_to_end(key)
    if len(L1_CACHE) > MAX_L1_ENTRIES:
        L1_CACHE.popitem(last=False)    # evict least-recently-used
        
def sample_cell(bounds: tuple[float, float, float, float], sample_lon: float, sample_lat: float) -> tuple[int, int]:
    min_lon, min_lat, max_lon, max_lat = bounds
    H, W = GRID_SHAPE
    col = int(np.clip((sample_lon - min_lon) / (max_lon - min_lon) * W, 0, W - 1))
    row = int(np.clip((max_lat - sample_lat) / (max_lat - min_lat) * H, 0, H - 1))
    return row, col

def destination(lat: float, lng: float, distance_km: float, bearing_deg: float) -> tuple[float, float]:
    dlat = (distance_km * math.cos(math.radians(bearing_deg))) / (METERS_PER_DEG_LAT / 1000.0)
    dlon = (distance_km * math.sin(math.radians(bearing_deg))) / (
        (METERS_PER_DEG_LAT / 1000.0) * math.cos(math.radians(lat))
    )
    return lat + dlat, lng + dlon

def compute_terrain_bias(lat: float, lng: float) -> list[dict]:
    """
    Returns N_BEARINGS {bearing_deg, factor} entries, factor averaging to ~1.0 across
    all bearings - relative reshaping multiplier, not absolute shape.
    Wind driven ROS formula on client still sets overall size. This just distorts the shape
    toward real uphill/fuel-type tendencies
    """
    fuel_weights = load_fuel_base_weights()
    grids = fetch_terrain_grids(lat, lng)
    bounds = grids["bounds"]
    
    raw_factors = []
    for i in range(N_BEARINGS):
        bearing = (360.0 / N_BEARINGS) * i
        sample_lat, sample_lon = destination(lat, lng, SAMPLE_RADIUS_KM, bearing)
        row, col = sample_cell(bounds, sample_lon, sample_lat)
        
        slope_deg = float(grids["slope"][row, col])
        aspect_deg = float(grids["aspect"][row, col])   # convention: direction slope faces (downhill)
        landcover_class = int(grids["landcover"][row, col])
        
        uphill_bearing = (aspect_deg + 180.0) % 360.0
        alignment = math.cos(math.radians(bearing - uphill_bearing))    # 1 = uphill, 2 = downhill
        slope_factor = 1.0 + 1.2 * math.tan(math.radians(min(slope_deg, 60.0))) * alignment
        slope_factor = max(0.3, min(3.0, slope_factor))
        
        fuel_weight = fuel_weights.get(landcover_class, 0.2)
        landcover_factor = 0.4 + 1.2 * fuel_weight
        
        raw_factors.append(slope_factor * landcover_factor)
        
    mean_factors = sum(raw_factors) / len(raw_factors) or 1.0
    return [
        {"bearing_deg": (360.0 / N_BEARINGS) * i, "factor": raw_factors[i] / mean_factors}
        for i in range(N_BEARINGS)
    ]