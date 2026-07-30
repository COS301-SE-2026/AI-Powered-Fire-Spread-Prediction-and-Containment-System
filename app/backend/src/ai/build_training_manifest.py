import argparse
import csv
import math
import os
from pathlib import Path

import httpx
import pandas as pd
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

    tile_name = f"Copernicus_DSM_COG_10_{lat_str}_{lon_str}_DEM"
    path = f"/vsis3/copernicus-dem-30m/{tile_name}/{tile_name}.tif"

    # warn if the bbox is to close to a degree boundary as it mightr need a second boundarty
    if(min_lat < tile_lat + 0.05 or max_lat > tile_lat + 0.95 or min_lon < tile_lon + 0.05 or max_lon > tile_lon + 0.95):
        print(f"Warning bbox ({min_lon:.3f}, {min_lat:.3f})-({max_lon:.3f},{max_lat:.3f})" f"is close to the DEM tile boundary")

    return path

def fetch_sent2_fire(fire_id: int, min_lon: float, min_lat: float, max_lon: float, max_lat: float, fire_start, days_before: int = 60, max_cloud_cover: int = 30) -> dict[str, str] | None:
    # find and download the least cloudy sent 2 data covering a fires bbox

    end_date = pd.Timestamp(fire_start) - pd.Timedelta(days=1)
    start_date = pd.Timestamp(fire_start) - pd.Timedelta(days=days_before)
    data_range = f"{start_date:%Y-%m-%d}/{end_date:%Y-%m-%d}"

    catalog = Client.open("https://earth-search.aws.element84.com/v1")
    search = catalog.search(
        collections=["sentinel-2-c1-l2a"],
        bbox=[min_lon,min_lat, max_lon, max_lat],
        datetime=data_range,
        query={"eo:cloud_cover": {"lt": max_cloud_cover}},
        max_items=1,
        sortby=[{"field": "properties.eo:cloud_cover", "direction": "asc"}]
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

def build_manifest(csv_path: str, out_path: str, top_n: int = 30, min_ticks: int = 2, max_gap_km: float = 5.0, max_gap_days: float = 4.0):
    OUTPUTDIR.mkdir(parents=True, exist_ok=True)

    events = inspect_fire_events(csv_path, max_gap_km=max_gap_km, max_gap_days=max_gap_days, min_ticks=min_ticks, limit=0)

    selected=events[:top_n]

    rows_written = 0

    with open(out_path, "w", newline="") as fire:
        writer = csv.writer(fire)
        writer.writerow(["fire_id", "b04_path", "b08_path", "b11_path", "dem_path", "worldcover_path", "scl_path"])

        for event in selected:
            fire_start = event.ticks[0]
            sentinel_paths = fetch_sent2_fire(event.fire_id, event.min_lon, event.min_lat, event.max_lon, event.max_lat, fire_start=fire_start)

            if sentinel_paths is None:
                continue

            dem_path = dem_vsis3_path(event.min_lon, event.min_lat, event.max_lon, event.max_lat)

            writer.writerow([
                event.fire_id,
                sentinel_paths["b04"], sentinel_paths["b08"], sentinel_paths["b11"],
                dem_path,
                "",
                "",
            ])

            rows_written += 1

    print(f"\n wrote {rows_written}/{len(selected)} manifest rows to {out_path}")

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", default="app/datasets/raw_data/static_manifest.csv")
    ap.add_argument("--top-n", type=int, default=30)
    ap.add_argument("--min-ticks", type=int, default=2)
    ap.add_argument("--max-gap-km", type=float, default=5.0)
    ap.add_argument("--max-gap-days", type=float, default=4.0)
    ap.add_argument("--limit", type=int, default=20, help="max fire events to print 0 = all fires")
    args = ap.parse_args()
    
    build_manifest(args.csv, args.out, args.top_n, args.min_ticks, args.max_gap_km, args.max_gap_days)


if __name__ == "__main__":
        main()