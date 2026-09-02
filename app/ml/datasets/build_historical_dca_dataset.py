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

