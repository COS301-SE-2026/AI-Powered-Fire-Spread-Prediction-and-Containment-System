import json
from pathlib import Path
import numpy as np
import rasterio
from rasterio.enums import Resampling

WEIGHTS_JSON = "processed/worldcover_base_weights.json"

#fallback if json not load
FUEL_BASE_WEIGHTS = {
    10: 0.90, # Tree cover
    20: 0.60, # Shrubland
    30: 0.40, # Grassland
    40: 0.30, # Cropland
    50: 0.00, # Built-up
    60: 0.10, # Bare / sparse vegetation
    70: 0.00, # Snow and ice
    80: 0.00, # Permanent water bodies
    90: 0.35, # Herbaceous wetland
    95: 0.50, # Mangroves
    100: 0.15# Moss and lichen
}

def load_fuel_base_weights() -> dict[int, float]:
    """load baseline fuel, calculated from LANDFIRE rulesets in calculate_ruleset_weights"""
    json_file = Path(WEIGHTS_JSON)
    if json_file.exists():
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
                return {int(k): float(v) for k, v in data.items()}
        except Exception as e:
            print(f"Could not parse {WEIGHTS_JSON} ({e}). Use default weights")
    return FUEL_BASE_WEIGHTS

def extract_worldcover_features(
        map_path: str,
        ndvi_path: str,
        swir_path: str,
        target_shape: tuple[int, int]
) -> dict[str, np.ndarray]:
    """Converts ESA WorldCover GeoTIFF layers into float32 matrices matching target grid dims (H, W)
    return dict containing fuel_load and dryness arrays from 0 to 1"""
    H, W = target_shape

    def read_layer(file_path: str, is_categorical: bool = False) -> np.ndarray:
        with rasterio.open(file_path) as src:
            method = Resampling.nearest if is_categorical else Resampling.bilinear
            return src.read(1, out_shape=(H, W), Resampling=method)
        
    raw_map = read_layer(map_path, is_categorical=True)
    fuel_base = np.zeros(raw_map.shape, dtype=np.float32)
    for class_val, weight in FUEL_BASE_WEIGHTS.items():
        fuel_base[raw_map == class_val] = weight

    #NDVI modifier
    raw_ndvi = read_layer(ndvi_path).astype(np.float32)
    ndvi_scale = np.clip((raw_ndvi - 30.0) / 220.0, 0.0, 1.0)

    #final hybrid fuel load
    fuel_load = fuel_base * ndvi_scale

    #dryness through swir
    raw_swir = read_layer(swir_path).astype(np.float32)
    dryness = np.clip(raw_swir / 250.0, 0.0, 1.0).astype(np.float32)

    return {
        "fuel_load" : fuel_load,
        "dryness" : dryness
    }