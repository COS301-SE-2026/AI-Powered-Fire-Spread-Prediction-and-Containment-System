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