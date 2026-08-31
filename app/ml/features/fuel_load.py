import json
import math
from pathlib import Path
from typing import Optional

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.io import MemoryFile
from rasterio.merge import merge as rio_merge
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds

from ml.features.geo_utils import stream_cropped_raster, OPTIMIZED_GDAL_ENV

# Sen2Cor Scene Classification vals, published in 'scl' asset.
# Use it to mask pixx\els that would otherwise silently corrupt

SCL_NO_DATA = 0
SCL_SATURATED_DEFECTIVE = 1
SCL_DARK_AREA = 2
SCL_CLOUD_SHADOW = 3
SCL_VEGETATION = 4
SCL_BARE_SOIL = 5
SCL_WATER = 6
SCL_UNCLASSIFIED = 7
SCL_CLOUD_MEDIUM_PROB = 8
SCL_CLOUD_HIGH_PROB = 9
SCL_THIN_CIRRUS = 10
SCL_SNOW_ICE = 11

# classes should be excluded from fuel and dryness calculations
DEFAULT_SCL_MASKED_CLASSES = frozenset(
    {
        SCL_NO_DATA,
        SCL_SATURATED_DEFECTIVE,
        SCL_CLOUD_SHADOW,
        SCL_CLOUD_MEDIUM_PROB,
        SCL_CLOUD_HIGH_PROB,
        SCL_THIN_CIRRUS,
    }
)

WEIGHTS_JSON = "processed/worldcover_base_weights.json"

# fallback if json not load
FUEL_BASE_WEIGHTS = {
    10: 0.90,  # Tree cover
    20: 0.60,  # Shrubland
    30: 0.40,  # Grassland
    40: 0.30,  # Cropland
    50: 0.00,  # Built-up
    60: 0.10,  # Bare / sparse vegetation
    70: 0.00,  # Snow and ice
    80: 0.00,  # Permanent water bodies
    90: 0.35,  # Herbaceous wetland
    95: 0.50,  # Mangroves
    100: 0.15,  # Moss and lichen
}

# ESA WorldCover on AWS Registry of Open Data
# https://registry.opendata.aws/esa-worldcover/
# tiles 3x3 degree COGs named by the lat/lon of their SW corner, of their SW corner

WORLDCOVER_BUCKET = "esa-worldcover"
WORLDCOVER_VERSIONS = {2020: "v100", 2021: "v200"}

# not od full directory/file listings or refetching overlapping bytes
S3_READ_ENV = dict(
    AWS_NO_SIGN_REQUEST="YES",
    GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF,.tiff",
    GDAL_HTTP_MULTIPLEX="YES",
    VSI_CACHE="TRUE",
    VSI_CACHE_SIZE=64_000_000,
    GDAL_CACHEMAX=64,
)


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


def worldcover_tile_id(lat: float, lon: float) -> str:
    """ESA WorldCover 3x3 degree tileid for a lat/lon"""
    tile_lat = int(math.floor(lat / 3.0) * 3)
    tile_lon = int(math.floor(lon / 3.0) * 3)
    ns = "N" if tile_lat >= 0 else "S"
    ew = "E" if tile_lon >= 0 else "W"
    return f"{ns}{abs(tile_lat):02d}{ew}{abs(tile_lon):03d}"


def worldcover_s3_urls_for_bbox(
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    year: int = 2021,
) -> list[str]:
    """build s3 COG URL covering bbox from public esa-worldcover bucket.
    If bbox over 3-deg tile boundary resolves multiple tiles"""
    if year not in WORLDCOVER_VERSIONS:
        raise ValueError(
            f"No known WorldCover version for year={year}"
            f"Available: {sorted(WORLDCOVER_VERSIONS)}"
        )
    version = WORLDCOVER_VERSIONS[year]

    lat0 = int(math.floor(min_lat / 3.0) * 3)
    lat1 = int(math.floor(max_lat / 3.0) * 3)
    lon0 = int(math.floor(min_lon / 3.0) * 3)
    lon1 = int(math.floor(max_lon / 3.0) * 3)

    tiles = {
        worldcover_tile_id(lat + 0.5, lon + 0.5)
        for lat in range(lat0, lat1 + 1, 3)
        for lon in range(lon0, lon1 + 1, 3)
    }
    return [
        f"s3://{WORLDCOVER_BUCKET}/{version}/{year}/map/ESA_WorldCover_10m_{year}_{version}_{tile}_Map.tif"
        for tile in sorted(tiles)
    ]


def _resample_to_shape(
    arr: np.ndarray, transform, crs, out_shape: tuple[int, int], resampling: Resampling
) -> np.ndarray:
    """Resample in-mem array to out_shape, so reuse rasterio's resampling kernels"""
    h, w = arr.shape[-2], arr.shape[-1]
    profile = {
        "driver": "GTiff",
        "height": h,
        "width": w,
        "count": 1,
        "dtype": arr.dtype,
        "crs": crs,
        "transform": transform,
    }
    with MemoryFile() as memfile:
        with memfile.open(**profile) as dst:
            dst.write(arr[0] if arr.ndim == 3 else arr, 1)
        with memfile.open() as dst:
            return dst.read(1, out_shape=out_shape, resampling=resampling)


def _read_window_single(
    file_path: str,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    out_shape: tuple[int, int],
    resampling: Resampling,
) -> np.ndarray:
    """Read from single / remote bucket.
    Only fetches the bytes covering the window"""
    with rasterio.open(file_path) as src:
        if src.crs is not None and src.crs.to_epsg() != 4326:
            b_min_lon, b_min_lat, b_max_lon, b_max_lat = transform_bounds(
                "EPSG:4326", src.crs, min_lon, min_lat, max_lon, max_lat
            )
        else:
            b_min_lon, b_min_lat, b_max_lon, b_max_lat = (
                min_lon,
                min_lat,
                max_lon,
                max_lat,
            )
        window = from_bounds(
            b_min_lon, b_min_lat, b_max_lon, b_max_lat, transform=src.transform
        )
        return src.read(1, window=window, out_shape=out_shape, resampling=resampling)


def _read_worldcover_window(
    worldcover_map_path: Optional[str],
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    out_shape: tuple[int, int],
    worldcover_year: int = 2021,
) -> np.ndarray:
    """Read categorical wordlcover raster cropped to bbox"""
    if worldcover_map_path is not None:
        return stream_cropped_raster(
            worldcover_map_path, min_lon, min_lat, max_lon, max_lat, out_shape, Resampling.nearest
        )

    urls = worldcover_s3_urls_for_bbox(
        min_lon, min_lat, max_lon, max_lat, year=worldcover_year
    )

    with rasterio.Env(**OPTIMIZED_GDAL_ENV):
        datasets = [rasterio.open(u) for u in urls]
        try:
            # merge crops to bbox part of moaic
            # only stream windows we need
            mosaic, out_transform = rio_merge(
                datasets,
                bounds=(min_lon, min_lat, max_lon, max_lat),
            )
            crs = datasets[0].crs
        finally:
            for ds in datasets:
                ds.close()
        
    if mosaic.shape[-2:] == out_shape:
        return mosaic[0]
    return _resample_to_shape(mosaic, out_transform, crs, out_shape, Resampling.nearest)


# sentinal 2 on aws store raw digital nrs
S2_REFLECTANCE_SCALE = 0.0001
S2_REFLECTANCE_OFFSET = -0.1
S2_NODATA_DN = 0


def _dn_to_reflectance(
    dn: np.ndarray,
    scale: float = S2_REFLECTANCE_SCALE,
    offset: float = S2_REFLECTANCE_OFFSET,
    nodata: int = S2_NODATA_DN,
) -> np.ndarray:
    """Convert raw sentinal2 dig nrs to surface reflectance"""
    refl = dn.astype(np.float32) * scale + offset
    if nodata is not None:
        refl = np.where(dn == nodata, np.nan, refl)
    return refl


def process_sentinal2_and_worldcover(
    b04_path: str,  # red band
    b08_path: str,  # NIR band
    b11_path: str,  # SWIR1 band
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    worldcover_map_path: Optional[str] = None,
    worldcover_year: int = 2021,
    target_shape: tuple[int, int] = (200, 200),
    s2_reflectance_scale: float = S2_REFLECTANCE_SCALE,
    s2_reflectance_offset: float = S2_REFLECTANCE_OFFSET,
    scl_path: Optional[str] = None,
    scl_masked_classes: frozenset[int] = DEFAULT_SCL_MASKED_CLASSES,
) -> dict[str, np.ndarray]:
    """Crops ESA worldcover and sentinal-2 band rasters to bonding box,
    resample to match (H, W), and calc fuel_load and dryness matrices"""

    H, W = target_shape
    fuel_weights = load_fuel_base_weights()

    wc_map = _read_worldcover_window(
        worldcover_map_path,
        min_lon,
        min_lat,
        max_lon,
        max_lat,
        out_shape=(H, W),
        worldcover_year=worldcover_year,
    )

    fuel_base = np.zeros((H, W), dtype=np.float32)
    for class_val, weight in fuel_weights.items():
        fuel_base[wc_map == class_val] = weight

    b04_dn = stream_cropped_raster(b04_path, min_lon, min_lat, max_lon, max_lat, (H, W), Resampling.bilinear)
    b08_dn = stream_cropped_raster(b08_path, min_lon, min_lat, max_lon, max_lat, (H, W), Resampling.bilinear)
    b11_dn = stream_cropped_raster(b11_path, min_lon, min_lat, max_lon, max_lat, (H, W), Resampling.bilinear)

    cloud_mask = None
    if scl_path is not None:
        scl = stream_cropped_raster(
            scl_path,
            min_lon,
            min_lat,
            max_lon,
            max_lat,
            (H, W),
            Resampling.nearest,
        )
        cloud_mask = np.isin(
            scl, np.array(sorted(scl_masked_classes), dtype=scl.dtype)
        )

    b04 = _dn_to_reflectance(b04_dn, s2_reflectance_scale, s2_reflectance_offset)
    b08 = _dn_to_reflectance(b08_dn, s2_reflectance_scale, s2_reflectance_offset)
    b11 = _dn_to_reflectance(b11_dn, s2_reflectance_scale, s2_reflectance_offset)

    if cloud_mask is not None:
        b04 = np.where(cloud_mask, np.nan, b04)
        b08 = np.where(cloud_mask, np.nan, b08)
        b11 = np.where(cloud_mask, np.nan, b11)

    # don't div by zero preventative
    eps = 1e-6

    ndvi = (b08 - b04) / (b08 + b04 + eps)
    ndvi_scale = np.clip((ndvi - 0.1) / 0.7, 0.0, 1.0)

    fuel_load = np.clip(fuel_base * ndvi_scale, 0.0, 1.0).astype(np.float32)
    if cloud_mask is not None:
        valid = ~cloud_mask
        fill_val = np.nanmean(np.where(valid, fuel_load, np.nan)) if valid.any() else 0.0
        fuel_load = np.where(np.isnan(fuel_load) | cloud_mask, fill_val, fuel_load)
    else:
        fuel_load = np.nan_to_num(fuel_load, nan=0.0)

    ndmi = (b08 - b11) / (b08 + b11 + eps)

    dryness = np.clip((1.0 - ndmi) / 2.0, 0.0, 1.0).astype(np.float32)
    if cloud_mask is not None:
        valid = ~cloud_mask
        fill_val = np.nanmean(np.where(valid, dryness, np.nan)) if valid.any() else 0.0
        dryness = np.where(np.isnan(dryness) | cloud_mask, fill_val, dryness)
    else:
        dryness = np.nan_to_num(dryness, nan=0.0)

    if cloud_mask is not None:
        valid_mask = ~cloud_mask
    else:
        valid_mask = np.ones((H, W), dtype=bool)

    return {
        "fuel_load": fuel_load,
        "dryness": dryness,
        "valid_mask": valid_mask,
    }
