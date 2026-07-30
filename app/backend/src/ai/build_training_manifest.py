import argparse
import csv
import math
import os
from pathlib import Path

import httpx
from pystac_client import Client

from .inspect_fire import inspect_fire_events

OUTPUTDIR = Path("app/datasets/raw_data")

os.environ.setdefault("AWS_NO_SIGN_REQUEST", "YES")

def dem_vsis3_path(min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> str:

    center_lat = (min_lat + max_lat) / 2.0
    center_lon = (min_lon + max_lon) / 2.0

    tile_lat = math.floor(center_lat)
    tile_lon = math.floor(center_lon)

    ns = "N" if tile_lat >= 0 else "S"
    ew = "E" if tile_lon >= 0 else "W"

    lat_str = f"{ns}{abs(tile_lat):02d}_00"
    lon_str = f"{ew}{abs(tile_lon):03d}_00"

    tile_name = f"Copernicus_DSM_COG_10_{lat_str}_{lon_str}"
    path = f"/vsis3/copernicus-dem-30m/{tile_name}/{tile_name}.tif"

    # warn if the bbox is to close to a degree boundary as it mightr need a second boundarty
    if(min_lat < tile_lat + 0.05 or max_lat > tile_lat + 0.95 or min_lon < tile_lon + 0.05 or max_lon > tile_lon + 0.95):
        print(f"Warning bbox ({min_lon:.3f}, {min_lat:.3f})-({max_lon:.3f},{max_lat:.3f})" f"is close to the DEM tile boundary")

    return path

def fetch_sent2_fire(fire_id: int, min_lon: float, min_lat: float, max_lon: float, max_lat: float, data_range: str = "2024-01-01/2025-06-01", max_cloud_cover: int = 30) -> dict[str, str] | None:
    # find and download the least cloudy sent 2 data covering a fires bbox

    catalog = Client.open("https://earth-search.aws.element84.com/v1")
    search = catalog.search(
        collections=["sentinel-2-c1-l2a"],
        bbox=[min_lon,min_lat, max_lon, max_lat],
        datetime=data_range,
        query={"eo:cloud_cover": {"lt": max_cloud_cover}},
        max_items=1,
        sortby=[{"field": "properties.eo:cloud_cover", "directions": "asc"}]
    )

    items = list(search.items())
    if not items:
        print(f"skip fire id: {fire_id}: no sent 2 scene under the max cloud cover of {max_cloud_cover}%")
        return None

    item = items[0]
    print(f"Fire ID: {fire_id} | using scene {item.id} with cloud cover {item.properties.get('eo:cloud_cover'):.1f}%")

    paths = {}
    for asset_key, suffix in [("red", "b04"), ("nir", "b08"), ("swir16", "b11")]:
        if asset_key not in item.assets:
            print(f"SKIP Fire ID: {fire_id} | missing asset '{asset_key}' in scene")
            return None

        target = OUTPUTDIR / f"fire_{fire_id}_{suffix}.tif"
        with httpx.stream("GET", item.assets[asset_key].href, follow_redirects=True, timeout=60.0) as r:
            r.raise_for_status()
            with open(target, "wb") as f:
                for chunk in r.iter_bytes(8192):
                    f.write(chunk)
            paths[suffix] = str(target)
    return paths