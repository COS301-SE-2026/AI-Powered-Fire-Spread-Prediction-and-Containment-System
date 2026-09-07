import rasterio
from rasterio.windows import from_bounds
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds
import numpy as np

OPTIMIZED_GDAL_ENV = dict(
    AWS_NO_SIGN_REQUEST="YES",
    GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF,.tiff",
    GDAL_HTTP_MULTIPLEX="YES",
    GDAL_HTTP_VERSION="2",
    VSI_CACHE="TRUE",
    VSI_CACHE_SIZE=64000000,
    GDAL_CACHEMAX=64
)

def stream_cropped_raster(
        file_path: str,
        min_lon: float,
        min_lat: float,
        max_lon: float,
        max_lat: float,
        out_shape: tuple[int, int],
        resampling: Resampling = Resampling.bilinear
) -> np.ndarray:
    """
    Streams only the pixels inside the bounding boc from a remote COG and resizes it to the target shape
    """

    with rasterio.Env(**OPTIMIZED_GDAL_ENV):
        with rasterio.open(file_path) as src:
            if src.crs is not None and src.crs.to_epsg() != 4326:
                b_min_lon, b_min_lat, b_max_lon, b_max_lat = transform_bounds(
                    "EPSG:4326", src.crs, min_lon, min_lat, max_lon, max_lat
                )
            else:
                b_min_lon, b_min_lat, b_max_lon, b_max_lat = min_lon, min_lat, max_lon, max_lat

            window = from_bounds(b_min_lon, b_min_lat, b_max_lon, b_max_lat, transform=src.transform)

            return src.read(
                1,
                window=window,
                out_shape=out_shape,
                resampling=resampling
            )