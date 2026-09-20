import asyncio
import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.backend.main import app
from app.backend.src.ai.cache import client as real_cache_client
from app.backend.src.routes.geo.water_bodies import (
    CACHE_TTL_SECONDS,
    OVERPASS_ENDPOINTS,
    build_query,
    cache_key,
    query_overpass,
)

MODULE = "app.backend.src.routes.geo.water-bodies"

VALID_BBOX = dict(min_lat=-26.0, min_lng=28.0, max_lat=-25.9, max_lng=28.1, min_area_m2=2000)

SAMPLE_OVERPASS_RESPONSE = {
    "elements": [
        {
            "type": "way",
            "id": 987654,
            "tags": {"name": "Integration Test Dam", "water": "reservoir"},
            "geometry": [
                {"lat": -25.95, "lon": 28.05},
                {"lat": -25.95, "lon": 28.06},
                {"lat": -25.96, "lon": 28.06},
                {"lat": -25.96, "lon": 28.05},
                {"lat": -25.96, "lon": 28.05},
            ],
        }
    ]
}

@pytest.fixture
def client():
    return TestClient(app)

# Test route wiring
class TestRouteRegistration:
    def test_water_bodies_route_is_registered_on_the_real_app(self):
        matching = [r for r in app.routes if getattr(r, "path", None) == "/api/geo/water-bodies"]
        assert matching, "water-bodies route not found on app - check routes/__init__.py wiring"
        assert "GET" in matching[0].methods