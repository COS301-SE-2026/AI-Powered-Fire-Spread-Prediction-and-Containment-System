import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.enums import Resampling

def crop_veg_bounding_box(
        min_lon: float, min_lat: float,
        max_lon: float, max_lat: float,
        map_path: str, ndvi_path: str, swir_path: str,
        target_shape: tuple[int, int] = (200, 200)
) -> dict[str, np.ndarray]:
    """Crops and resampled veg feature arrays matching lat/lon bounding box"""

    H, W = target_shape

    def read_window(file_path: str, is_categorical: bool = False) -> np.ndarray:
        with rasterio.open(file_path) as src:
            #lat lon pixels to window
            window = from_bounds(min_lon, min_lat, max_lon, max_lat, transform=src.transform)

            #read and resample sub-region into target array dim (H, W)
            resample_method = Resampling.nearest if is_categorical else Resampling.bilinear
            return src.read(1, window=window, out_shape=(H, W), resampling=resample_method)
        
    wc_grid = read_window(map_path, is_categorical=True)
    ndvi_grid = read_window(ndvi_path).astype(np.float32)
    swir_grid = read_window(swir_path).astype(np.float32)

    base_weight_grid = np.zeros(wc_grid.shape, dtype=np.float32)
    for class_id, weight in FUEL_BASE_WEIGHTS.items():
        base_weight_grid[wc_grid == class_id] = weight

    #final 2d matrices bound to box
    ndvi_scale = np.clip((ndvi_grid - 30.0) / 220.0, 0.0, 1.0)
    fuel_load_matrix = np.clip(base_weight_grid * ndvi_scale, 0.0, 1.0).astype(np.float32)
    dryness_matrix = np.clip(swir_grid / 2250.0, 0.0, 1.0).astype(np.float32)

    return {
        "fuel_load": fuel_load_matrix,
        "dryness": dryness_matrix
    }