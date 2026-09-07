# calculates elevation slope and aspect
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import from_bounds
import math
from app.backend.ml.features.geo_utils import stream_cropped_raster

DEMREADENV = dict(
    AWS_NO_SIGN_REQUEST="YES",
    GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF,.tiff",
)

METERS_PER_DEG_LAT = 111320.0 # the amount of meters that 1 latitude on earth is equal to

def bbox_cell_size_m(
        min_lon: float,
        min_lat: float,
        max_lon: float,
        max_lat: float,
        H: int,
        W: int
) -> tuple[float, float]:
    """
    The real ground size of one grid cell in meters, given the boundary box and the (H,W). Longitude degrees shrink with latitude.
    """
    lat_center = (min_lat + max_lat) / 2
    m_per_deg_lon = METERS_PER_DEG_LAT * math.cos(math.radians(lat_center))

    # height and width in meters for total grid size
    height = (max_lat - min_lat) * METERS_PER_DEG_LAT
    width = (max_lon - min_lon) * m_per_deg_lon

    cell_size_y = height / H
    cell_size_x = width / W

    return cell_size_y, cell_size_x

def extract_terrain_features(
    dem_path: str,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    target_shape: tuple[int, int] = (64, 64),
) -> dict[str, np.ndarray]:
    """Read elevation DEM GeoTIFF and computes elevation, slope and aspect array"""

    H, W = target_shape

    elevation = stream_cropped_raster(
        dem_path, min_lon, min_lat, max_lon, max_lat, target_shape
    ).astype(np.float32)

    cell_size_y, cell_size_x = bbox_cell_size_m(min_lon, min_lat, max_lon, max_lat, H, W)

    # compute elevation gradients along rows and columns seperately
    dy, dx = np.gradient(elevation, cell_size_y, cell_size_x)

    # compute slope in degrees between 0 and 90 degrees
    slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
    slope = np.degrees(slope_rad).astype(np.float32)

    # aspect degrees between 0 and 360 degrees
    aspect = (np.degrees(np.arctan2(-dx, dy)) % 360.0).astype(np.float32)

    return {"elevation": elevation, "slope": slope, "aspect": aspect}
