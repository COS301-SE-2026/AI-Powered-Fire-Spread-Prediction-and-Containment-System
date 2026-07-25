import json
from pathlib import Path
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import from_bounds

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

def process_sentinal2_and_worldcover(
        worldcover_map_path: str,
        b04_path: str, #red band
        b08_path: str, #NIR band
        b11_path: str, #SWIR1 band
        min_lon: float, min_lat: float,
        max_lon: float, max_lat: float,
        target_shape: tuple[int, int] = (200, 200)
) -> dict[str, np.ndarray]:
    """Crops ESA worldcover and sentinal-2 band rasters to bonding box, 
    resample to match (H, W), and calc fuel_load and dryness matrices"""

    H, W = target_shape
    fuel_weigths = load_fuel_base_weights()

    def read_window(file_path: str, is_categorical: bool = False) -> np.ndarray:
        with rasterio.open(file_path) as src:
            #lat lon pixels to window
            window = from_bounds(min_lon, min_lat, max_lon, max_lat, transform=src.transform)

            #read and resample sub-region into target array dim (H, W)
            resample_method = Resampling.nearest if is_categorical else Resampling.bilinear
            return src.read(1, window=window, out_shape=(H, W), resampling=resample_method)
        
    wc_map = read_window(worldcover_map_path, is_categorical=True)
    fuel_base = np.zeros((H, W), dtype=np.float32)
    for class_val, weight in fuel_weigths.items():
        fuel_base[wc_map == class_val] = weight

    b04 = read_window(b04_path)
    b08 = read_window(b08_path)
    b11 = read_window(b11_path)

    #prevent div by 0
    eps = 1e-6

    ndvi = (b08 - b04) / (b08 + b04 + eps)
    ndvi_scale = np.clip((ndvi - 0.1) / 0.7, 0.0, 1.0)

    fuel_load = np.clip(fuel_base * ndvi_scale, 0.0, 1.0).astype(np.float32)

    ndmi = (b08 - b11) / (b08 + b11 + eps)

    dryness = np.clip((1.0 - ndmi) / 2.0, 0.0, 1.0).astype(np.float32)

    return {
        "fuel_load": fuel_load,
        "dryness": dryness
    }