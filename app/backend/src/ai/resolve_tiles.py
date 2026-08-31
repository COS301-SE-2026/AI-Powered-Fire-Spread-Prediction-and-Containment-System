import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from pystac_client import Client

# The AWS data source
COPERNICUS_DEM_BUCKET = "copernicus-dem-30m"
STAC_API = "https://earth-search.aws.element84.com/v1"
S2_COLLECTION = "sentinel-2-c1-l2a"

# Optical bands we need for our feature extraction
S2_REQUIRED_BANDS = {
    "red",
    "nir",
    "swir16"
}

@dataclass
class ResolvedTiles:
    """Container to hold the remote raster URLS for the simulation"""
    b04_path: str
    b08_path: str
    b11_path: str
    dem_path: str
    scl_path: Optional[str] = None
    s2_item_id: Optional[str] = None
    s2_cloud_cover: Optional[float] = None

def dem_tile_id(lat: float, lon: float) -> str:
    """
    Generates Copernicus 30m DEM tiles using the naming convention:

    name dem tiles by 1deg cell SW corner e.g. lat=-25.9 lon=28.1 = S26_00_E028_00
    """
    tile_lon = math.floor(lon)
    lat_mag = abs(math.floor(lat))
    ns = "N" if lat >= 0 else "S"
    ew = "E" if tile_lon >= 0 else "W"

    return f"{ns}{lat_mag:02d}_00_{ew}{abs(tile_lon):03d}_00"

def resolve_dem_path(
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float
) -> list[str]:
    """
    Gets the 1x1 DEM tile raster path that overlaps the fires bounding box
    """
    lat0, lat1 = math.floor(min_lat), math.floor(max_lat)
    lon0, lon1 = math.floor(min_lon), math.floor(max_lon)

    tiles = {
        dem_tile_id(lat + 0.5, lon + 0.5)
        for lat in range (lat0, lat1 + 1)
        for lon in range (lon0, lon1 + 1)
    }

    return [
        f"/vsis3/{COPERNICUS_DEM_BUCKET}/Copernicus_DSM_COG_10_{tile}_DEM/"
        f"Copernicus_DSM_COG_10_{tile}_DEM.tif"
        for tile in sorted(tiles)
    ]

def resolve_sentinel2_bands(
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    when: Optional[datetime] = None,
    time_window: int = 14,
    max_cloud_coverage = 10.0
) -> ResolvedTiles:
    """
    Query the AWS STAC catalog to find the clearest image of the scene over the fire area
    """
    when = when or datetime.now(timezone.utc)
    bbox = [min_lon, min_lat, max_lon, max_lat]
    catalog = Client.open(STAC_API)

    date_start = (when - timedelta(days=time_window)).strftime("%Y-%m-%d")
    date_end = (when + timedelta(days=time_window)).strftime("%Y-%m-%d")

    items = []
    for cloud_limit in (max_cloud_coverage, 30.0, 100.0):
        search = catalog.search(
            collections=[S2_COLLECTION],
            bbox=bbox,
            datetime=f"{date_start}/{date_end}",
            query={"eo:cloud_cover": {"lt": cloud_limit}},
            max_items=20
        )
        items = list(search.items())
        if items:
            break

    if not items:
        raise FileNotFoundError(
            f"No sentinel2 scene found for boundary box={bbox} within {time_window}d of {when.date()}"
        )

    def score(item):
        item_dt = item.datetime if item.datetime else when
        time_delta = abs((item_dt - when).total_seconds())
        cloud = item.properties.get("eo:cloud_cover", 100)
        return (time_delta, cloud)

    best = min(items, key=score)
    assets = best.assets

    missing = [k for k in S2_REQUIRED_BANDS if k not in assets]
    if missing:
        raise FileNotFoundError(f"Scene {best.id} is missing required bands: {missing}")

    return ResolvedTiles(
        b04_path=assets["red"].href,
        b08_path=assets["nir"].href,
        b11_path=assets["swir16"].href,
        dem_path="",
        scl_path=assets["scl"].href if "scl" in assets else None,
        s2_item_id=best.id,
        s2_cloud_cover=best.properties.get("eo:cloud_cover")
    )

def resolve_tile_paths(
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    when: Optional[datetime] = None
) -> ResolvedTiles:
    """
    A wrapper that resolves the Sentinel-2 and DEM paths
    """
    
    s2 = resolve_sentinel2_bands(min_lon, min_lat, max_lon, max_lat, when=when)

    dem_paths = resolve_dem_path(min_lon, min_lat, max_lon, max_lat)
    s2.dem_path = dem_paths[0]

    if len(dem_paths) > 1:
        print(
            f"WARNING: bbox spans {len(dem_paths)} DEM tiles, only using first ({dem_paths[0]}) - terrain will be wrong near the edge"
        )

    return s2