"""
Supplements Mapbox's own vector tiles with damn/reservoir/pond data pulled from 
OpenStreetMap via Overpass API.

Purpose: Mapbox's default 'water' source-layer doesn't distinguish a farm damn from any other 
water polygon and simplifies away small featuress at lower zoom levels.
This endpoint queries OSM directly for tags that are specifically smaller water bodies 
that are small firefighter-relevant water sources are not silently dropped.

Results cached in Valkey keyed by a rounded bounding box, both to stay within Overpass's
fair-use limits and because this data rarely changes.
"""
import hashlib
import json
import math
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.backend.src.ai.cache import client as cache_client

router = APIRouter(prefix="/api/geo", tags=["Geo"])

# Public Overpass instances tried in order (main instance often under load so fallback to 
# mirrors rather than fail the request)

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

CACHE_TTL_SECONDS = 60 * 60 * 24 * 7
REQUEST_TIMEOUT_SECONDS = 25
MAX_BBOX_SIDE_DEG = 1.0

def build_query(min_lat: float, min_lng: float, max_lat: float, max_lng: float) -> str:
    bbox = f"{min_lat},{min_lng},{max_lat},{max_lng}"
    return f"""
    [out:json][timeout:{REQUEST_TIMEOUT_SECONDS}];
    (
        way["natural"="water"]["water"~"^(resevoir|pond|basin)$"]({bbox});
        way["landuse"="resevoir"]({bbox});
        way["waterway"="dam"]({bbox});
        node["waterway"="dam"]({bbox});
    );
    out geom;
    """
    
def planar_area_m2(coords: list[tuple[float, float]], ref_lat: float) -> float:
    """
    Approximate polygon area in m^2 using equirectangular projection centered on ref_lat.
    'Is this water source big enough to matter' type filter
    """
    if len(coords) < 3:
        return 0.0

    meters_per_deg_lat = 111_320.0
    meters_pre_deg_lng = 11_320.0 * math.cos(math.radians(ref_lat))

    projected = [(lng * meters_pre_deg_lng, lat * meters_per_deg_lat) for lng, lat in coords]
    
    # Shoelace formula
    toatl = 0.0
    n = len(projected)
    for i in range(n):
        x1, y1 = projected[i]
        x2, y2 = projected[(i + 1) % n]
        total += x1 * y2 - x2 * y1
    return abs(total) / 2.0

def cache_key(min_lat: float, min_lng: float, max_lat: float, max_lng: float, min_area_m2: float) -> str:
   # Round bbox so nearby/identical requests hit the same cache entry instead of each spawning a fresh Overpass call
   payload = {
       "min_lat": round(min_lat, 3),
       "min_lng": round(min_lng, 3),
       "max_lat": round(max_lat, 3),
       "max_lng": round(max_lng, 3),
       "min_area_m2": round(min_area_m2, 0),
   }
   encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
   digest = hashlib.sha256(encoded).hexdigest()[:20]
   return f"geo:water_bodies:{digest}"

async def query_overpass(query: str) -> dict:
    last_error: Optional[Exception] = None
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as http_client:
        for endpoint in OVERPASS_ENDPOINTS:
            try:
                resp = await http_client.post(endpoint, data={"data": query})
                resp.raise_for_status()
                return resp.json()
            except Exception as exc:
                last_error = exc
                continue
    raise HTTPException(status_code=502, details=f"Overpass query failed: {last_error}")

def elements_to_geojson(elements: list[dict], main_area_m2: float) -> dict:
    features = []
    
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name")
        source_tag = tags.get("water") or tags.get("landuse") or tags.get("waterway") or "water"
        
        if el["type"] == "way" and el.get("geometry"):
            coords = [(pt["lon"], pt["lat"]) for pt in el["geometry"]]
            if len(coords) < 3 or coords[0] != coords[-1]:
                # not a closed ring (eg. linear dam wall), represent it as a line instead
                if len(coords) >= 2:
                    features.append(
                        {
                            "type": "Feature",
                            "properties": {
                                "id": f"way/{el['id']}",
                                "name": name,
                                "source": source_tag,
                                "kind": "dam_wall",
                            },
                            "geometry": {"type": "LineString", "coordinates": coords},
                        }
                    )
                continue
            
            ref_lat = sum(lat for _, lat in coords) / len(coords)
            area_m2 = planar_area_m2(coords, ref_lat)
            if area_m2 < main_area_m2:
                continue
        
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "id": f"way/{el['id']}",
                        "name": name,
                        "source": source_tag,
                        "kind": "resevoir",
                        "areaHa": round(area_m2 / 10000, 2),
                    },
                    "geometry": {"type": "Polygon", "coordinates": [coords]},
                }
            )
            
        elif el["type"] == "node":
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "id": f"node/{el['id']}",
                        "name": name,
                        "source": source_tag,
                        "kind": "dam_point",
                    },
                    "geometry": {"type": "Point", "coordinates": [el["lon"], el["lat"]]},
                }
            )
        
    return {"type": "FeatureCollection", "features": features}


            
