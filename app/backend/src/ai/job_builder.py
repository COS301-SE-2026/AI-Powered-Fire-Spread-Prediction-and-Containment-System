import logging
import hashlib
import json
import os
import time
from pathlib import Path
import requests
import numpy as np
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# static grid
from app.backend.src.ai.resolve_tiles import resolve_dem_path, resolve_sentinel2_bands
from app.backend.ml.features.terrain import extract_terrain_features
from app.backend.ml.features.fuel_load import process_sentinal2_and_worldcover

log = logging.getLogger("job_builder")

class DataSourceError(Exception):
    """upstream data source error failed"""

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_HISTORY_LENGTH = 6

DEFAULT_DCA_PARAMS = {
    "a": 0.015,
    "p_h": 0.06,
    "c_1": 0.04,
    "c_2": 0.03,
    "p_continue": 0.6,
}

def http_session() -> requests.Session:
    """Retries request failures from openMeteo with backoff instead of failing a job"""
    retry = Retry(
        total=2,
        backoff_factor=1,
        backoff_max=4,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=False,
    )

    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session

_HTTP = http_session()

STATIC_CACHE_DIR = os.getenv("STATIC_CACHE_DIR")
STATIC_CACHE_TTL_S = int(os.getenv("STATIC_CACHE_TTL_S", str(24 * 3600)))

def static_cache_path(job: dict) -> Path | None:
    if not STATIC_CACHE_DIR:
        return None
    key = json.dumps(
        {"b": [round(v, 5) for v in job["grid_bounds"]], "h": job["grid_h"], "w": job["grid_w"]},
        sort_keys=True,
    )
    return Path(STATIC_CACHE_DIR) / f"static_{hashlib.sha256(key.encode()).hexdigest()[:20]}.npz"

def load_static_cache(path: Path | None) -> dict | None:
    try:
        if path and path.exists() and time.time() - path.stat().st_mtime < STATIC_CACHE_TTL_S:
            with np.load(path) as data:
                log.info("Static grids cache hit (%s)", path.name)
                return {k: data[k] for k in data.files}
    except Exception as err:
        log.warning("Static grids cache read failed (%s), refetching", err)
    return None

def save_static_cache(path: Path | None, grids: dict) -> None:
    if not path:
        return

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        with open(tmp, "wb") as f:
            np.savez_compressed(f, **grids)
        os.replace(tmp, path)
    except Exception as err:
        log.warning("Static grids cache write failed (%s)", err)

def fetch_weather_history(job: dict) -> list:
    """
    Fetches weather history length hours for fire's center points, and broadcasts each hourly point value across the (grid_h, grid_w) grid.
    """

    grid_h = job["grid_h"]
    grid_w = job["grid_w"]

    params = {
        "latitude": job["center_lat"],
        "longitude": job["center_lon"],
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m",
        "wind_speed_unit": "ms",
        "past_hours": WEATHER_HISTORY_LENGTH,
        "forecast_hours": 1,
        "timezone": "UTC"
    }

    try:
        response = _HTTP.get(OPEN_METEO_URL, params=params, timeout=10)
        response.raise_for_status()
        hourly = response.json()["hourly"]
    except (requests.exceptions.RequestException, ValueError, KeyError) as err:
        raise DataSourceError(f"Open-Meteo unavailable: {err}") from err

    n_available = len(hourly["time"])
    if n_available < WEATHER_HISTORY_LENGTH:
        raise DataSourceError(f"Open-Meteo returned {n_available} hours, need {WEATHER_HISTORY_LENGTH}")
    start = n_available - WEATHER_HISTORY_LENGTH

    frames = []
    for i in range(start, n_available):
        temperature_c = hourly["temperature_2m"][i]
        rel_humidity_pct = hourly["relative_humidity_2m"][i]
        wind_speed_ms = hourly["wind_speed_10m"][i]
        wind_direction_deg = hourly["wind_direction_10m"][i]

        direction_rad = np.radians(wind_direction_deg)
        wind_u = -wind_speed_ms * np.sin(direction_rad)
        wind_v = -wind_speed_ms * np.cos(direction_rad)

        frames.append(
            {
                "wind_u": np.full((grid_h, grid_w), wind_u, dtype=np.float32),
                "wind_v": np.full((grid_h, grid_w), wind_v, dtype=np.float32),
                "temperature": np.full((grid_h, grid_w), temperature_c, dtype=np.float32),
                "rel_humidity": np.full((grid_h, grid_w), rel_humidity_pct, dtype=np.float32)
            }
        )

    return frames


def fetch_static_grids(job: dict) -> dict:
    """
    Fetches static terrain and vegetation grids for the bounding boxes using existing project feature extraction
    """

    cache_path = static_cache_path(job)
    cached = load_static_cache(cache_path)
    if cached is not None:
        return cached

    min_lon, min_lat, max_lon, max_lat = job["grid_bounds"]
    target_shape = (job["grid_h"], job["grid_w"])

    dem_paths = resolve_dem_path(min_lon, min_lat, max_lon, max_lat)
    if len(dem_paths) > 1:
        log.warning(
            "bbox spans %d DEM tiles, only using firest (%s) - terrain may vary near boundary edge",
            len(dem_paths),
            dem_paths[0]
        )

    terrain = extract_terrain_features(dem_paths[0], min_lon, min_lat, max_lon, max_lat, target_shape=target_shape)

    aspect_rad = np.radians(terrain["aspect"])
    aspect_sin = np.sin(aspect_rad).astype(np.float32)
    aspect_cos = np.cos(aspect_rad).astype(np.float32)

    s2 = resolve_sentinel2_bands(min_lon, min_lat, max_lon, max_lat)

    vegetation = process_sentinal2_and_worldcover(
            b04_path=s2.b04_path,
            b08_path=s2.b08_path,
            b11_path=s2.b11_path,
            min_lon=min_lon,
            min_lat=min_lat,
            max_lon=max_lon,
            max_lat=max_lat,
            target_shape=target_shape,
            scl_path=s2.scl_path,
        )
        
    grids = {
        "elevation": terrain["elevation"],
        "slope": terrain["slope"],
        "aspect_sin": aspect_sin,
        "aspect_cos": aspect_cos,
        "fuel_load": vegetation["fuel_load"],
        "dryness": vegetation["dryness"],
        "nonburnable": vegetation["nonburnable"]
    }

    save_static_cache(cache_path, grids)
    return grids

def build_volunteer_payload(
    job_id: str,
    weather_history: list,
    static_grids: dict,
    ignition_mask: np.ndarray,
    cell_size_m: float,
    n_steps: int,
    grid_bounds: list[float],
    containment_lines: list[str],
    params: dict = None
) -> dict:
    """
    Serializes the preprocessed np grids into shape expected by client worker pipeline
    """
    return{
        "job_id": job_id,
        "weather_history": [
            [
                f["wind_u"].tolist(),
                f["wind_v"].tolist(),
                f["temperature"].tolist(),
                f["rel_humidity"].tolist(),
            ]
            for f in weather_history
        ],
        "static_grids": {k: v.tolist() for k, v in static_grids.items()},
        "ignition_mask": ignition_mask.tolist(),
        "cell_size_m": cell_size_m,
        "n_steps": n_steps,
        "grid_bounds": grid_bounds,
        "containment_lines": containment_lines,
        "params": params or DEFAULT_DCA_PARAMS
    }