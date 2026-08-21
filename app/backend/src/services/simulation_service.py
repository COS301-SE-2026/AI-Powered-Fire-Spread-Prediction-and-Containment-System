import asyncio
import logging
import math

import numpy as np
from fastapi import HTTPException

from app.backend.src.ai.dca import run_dca
from app.backend.src.ai.geo import bbox_from_fire, touch_edge
from app.backend.src.ai.resolve_tiles import resolve_tile_paths
from app.backend.src.ai.simulation import build_boundary_ignition_mask
from app.backend.src.ai.weather_bridge import WeatherForecastBridge
from app.ml.features.real_data_loader import load_real_inference_data

logger = logging.getLogger(__name__)

METRES_PER_DEG_LAT = 111_320.0
TARGET_CELL_SIZE_M = 15.0
MIN_GRID_DIMENSION = 10
MAX_GRID_DIMENSION = 800

DEFAULT_DCA_PARAMS = {
    "a": 0.015,
    "p_h": 0.06,
    "c_1": 0.04,
    "c_2": 0.03,
    "p_continue": 0.6,
}

def grid_dimensions_for_extent(
    lat_extent_deg: float, lon_extent_deg: float, lat: float, target_cell_size_m: float = TARGET_CELL_SIZE_M
) -> tuple[int, int]:
    """Calculates grid dimensions based on irl targer cell size"""
    lat_extent_m = lat_extent_deg * METRES_PER_DEG_LAT
    lon_extent_m = lon_extent_deg * METRES_PER_DEG_LAT * math.cos(math.radians(lat))
    grid_h = int(np.clip(round(lat_extent_m / target_cell_size_m), MIN_GRID_DIMENSION, MAX_GRID_DIMENSION))
    grid_w = int(np.clip(round(lon_extent_m / target_cell_size_m), MIN_GRID_DIMENSION, MAX_GRID_DIMENSION))

    return grid_h, grid_w

