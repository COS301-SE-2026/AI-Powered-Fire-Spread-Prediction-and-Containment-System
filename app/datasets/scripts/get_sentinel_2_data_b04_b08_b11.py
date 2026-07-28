#get sentinal 2 data in bandwidths b04 b08 b11
#only run once

from pathlib import Path
from pystac_client import Client
import httpx

OUTPUT_DIR = Path("app/datasets/raw_data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BBOX = [16.4, -34.90, 33, -22.1]
DATE_RANGE = "2024-01-01/2024-12-31"

print("Search Element84 Earth Search STAC API for Sentinel-2")
catalog = Client.open("https://earth-search.aws.element84.com/v1")

search = catalog.search(
    collections=["sentinel-2-c1-l2a"],
    bbox=BBOX,
    datetime=DATE_RANGE,
    query={"eo:cloud_cover": {"lt": 10}},
    max_items=1
)

items = list(search.items())
if not items:
    raise FileNotFoundError("No cloud free Sentinel-2 scenes found")

item = items[0]
print(f"Found scene: {item.id} (Cloud cover: {item.properties.get('eo:cloud_cover'):.1f}%)")

#needed for fuel_load.py
required_bands = {
    "red": OUTPUT_DIR / "b04.tif",
    "nir": OUTPUT_DIR / "b08.tif",
    "swir16": OUTPUT_DIR / "b11.tif"
}

for asset_key, target_path in required_bands.items():
    if asset_key in item.assets:
        download_url = item.assets[asset_key].href
        print(f"Download {asset_key} to {target_path.name}")

        with httpx.stream("GET", download_url, follow_redirects=True, timeout=60.0) as response:
            response.raise_for_status()
            with open(target_path, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)

print(f"Bands downloaded successfully")