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

MODULE = "app.backend.src.routes.geo.water_bodies"

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
        
# Test httpx client (fake wire - no functional-level mocking)
REAL_ASYNC_CLIENT = httpx.AsyncClient

def client_with_transport(handler):
    def factory(**kwargs):
        return REAL_ASYNC_CLIENT(transport=httpx.MockTransport(handler), timeout=kwargs.get("timeout"))
    
    return factory

class TestQueryOverpassRealHttpClient:
    def test_parses_a_successful_overpass_response(self):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.host == "overpass-api.de"
            return httpx.Response(200, json=SAMPLE_OVERPASS_RESPONSE)
        
        with patch(f"{MODULE}.httpx.AsyncClient", side_effect=client_with_transport(handler)):
            query = build_query(*[VALID_BBOX[k] for k in ("min_lat", "min_lng", "max_lat", "max_lng")])
            result = asyncio.run(query_overpass(query))
            
        assert result == SAMPLE_OVERPASS_RESPONSE
        
    def test_falls_back_to_second_mirror_when_first_fails(self):
        calls = []
        
        def handler(request: httpx.Request) -> httpx.Response:
            calls.append(request.url.host)
            if request.url.host == OVERPASS_ENDPOINTS[0].split("/")[2]:
                return httpx.Response(500, text="mirror down")
            return httpx.Response(200, json=SAMPLE_OVERPASS_RESPONSE)
        
        with patch(f"{MODULE}.httpx.AsyncClient", side_effect=client_with_transport(handler)):
            result = asyncio.run(query_overpass("fake query"))
        
        assert result == SAMPLE_OVERPASS_RESPONSE
        assert len(calls) == 2  # first mirror tried and failed, second succeeded
        
    def test_raises_http_exception_when_every_mirror_fails(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, text="down")
        
        with patch(f"{MODULE}.httpx.AsyncClient", side_effect=client_with_transport(handler)):
            with pytest.raises(HTTPException) as exc_info:
                asyncio.run(query_overpass("fake query"))
                
        assert exc_info.value.status_code == 502