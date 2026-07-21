import numpy as np
import rasterio
from rasterio.enums import Resampling

#use 0.5 for values for now, will change when get 
FUEL_BASE_WEIGHTS = {
    10: 0.5, # Tree cover
    20: 0.5, # Shrubland
    30: 0.5, # Grassland
    40: 0.5, # Cropland
    50: 0.5, # Built-up
    60: 0.5, # Bare / sparse vegetation
    70: 0.5, # Snow and ice
    80: 0.5, # Permanent water bodies
    90: 0.5, # Herbaceous wetland
    95: 0.5, # Mangroves
    100: 0.5# Moss and lichen
}

def extract_worldcover_features(
        map_path: str,
        ndvi_path: str,
        swir_path: str,
        target_shape: tuple[int, int]
) -> dict[str, np.ndarray]:
    """Converts ESA WorldCover GeoTIFF layers into float32 matrices matching target grid dims (H, W)"""
    H, W = target_shape

    def read_layer(file_path: str, is_categorical: bool = False) -> np.ndarry:
        with rasterio.open(file_path) as src:
            method = Resampling.nearest if is_categorical else Resampling.bilinear
            return src.read(1, out_shape=(H, W), Resampling=method)
        
    raw_map = read_layer(map_path, is_categorical=True)
    fuel_base = np.zeros(raw_map.shape, dtype=np.float32)
    for class_cal, weight in FUEL_BASE_WEIGHTS.items():
        fuel_base[raw_map == class_val] = weight

    #NDVI modifier
    raw_ndvi = read_layer(ndvi_path).astype(np.float32)
    ndvi_scale = np.clip((raw_ndvi - 30.0) / 220.0, 0.0, 1.0)

    #final hybrid fuel load
    fuel_load = fuel_base * ndvi_scale

    #dryness through swir
    raw_swir = read_layer(swir_path).astype(np.float32)
    dryness = np.clip(raw_swir / 250.0, 0.0, 1.0)

    return {
        "fuel_load" : fuel_load.astype(np.float32),
        "dryness" : dryness.astype(np.float32)
    }