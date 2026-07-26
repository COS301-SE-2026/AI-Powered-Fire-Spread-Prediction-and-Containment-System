import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import from_bounds

def extract_terrain_features(
        dem_path: str,
        min_lon: float, min_lat: float,
        max_lon: float, max_lat: float,
        target_shape: tuple[int, int] = (64, 64),
        cell_size_m: float = 30.0
) -> dict[str, np.ndarray]:
    """Read elevation DEM GeoTIFF and computes elevation, slope and aspect array"""

    H, W = target_shape

    with rasterio.open(dem_path) as src:
        window = from_bounds(min_lon, min_lat, max_lon, max_lat, transform=src.transform)
        elevation = src.read(1, window=window, out_shape=(H, W), resampling=Resampling.bilinear).astype(np.float32)

        #compute elevation gradients along rows and columns
        dy, dx = np.gradient(elevation, cell_size_m)

        #compute slope in degrees between 0 and 90 degrees
        slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
        slope = np.degrees(slope_rad).astype(np.float32)

        #aspect degrees between 0 and 360 degrees
        aspect = (np.degrees(np.arctan2(-dx, dy)) % 360.0).astype(np.float32)

        return{
            "elevation": elevation,
            "slope": slope,
            "aspect": aspect
        }
