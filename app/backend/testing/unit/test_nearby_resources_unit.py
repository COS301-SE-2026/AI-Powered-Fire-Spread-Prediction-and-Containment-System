from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.backend.db import get_db
from app.backend.main import app
from app.backend.src.enums.resource import ResourceStatus, ResourceType
from app.backend.src.enums.user_role import UserRole
from app.backend.src.schemas.resource import NearbyResourceResponse

# Test schema

class TestNearbyResourceResponseSchema:
    BASE = {
        "id": "res-1",
        "resource": "water_tank",
        "otherResource": "",
        "capacity": 5000,
        "capacityUnit": "liters",
        "otherCapacity": "",
        "status": "available",
        "availableFrom": "2026-09-20",
        "availableUntil": None,
        "location": "Farm on Old Warmbaths Rd, Pretoria North",
        "externalPin": {"lat": -25.7461, "lng": 28.1881},
        "name": "Pieter van der Merwe",
        "contact": "082 456 1234",
        "distance": 0.47,
    }
    
    def test_accepts_a_full_payload(self):
        r = NearbyResourceResponse.model_validate(self.BASE)
        assert r.distance == 0.47
        assert r.resource == ResourceType.water_tank
        assert r.status == ResourceStatus.available
        
    def test_distance_is_required(self):
        data = {k: v for k, v in self.BASE.items() if k != "distance"}
        with pytest.raises(ValidationError):
            NearbyResourceResponse.model_validate(data)
            
    def test_serialize_camelcase_with_distance(self):
        r = NearbyResourceResponse.model_validate(self.BASE)
        dumped = r.model_dump(by_alias=True)
        assert dumped["distance"] == 0.47
        assert dumped["externalPin"] == {"lat": -25.7461, "lng": 28.1881}
        assert "external_pin" not in dumped
        
# Test route
def fake_user(role):
    user = MagicMock()
    user.id = "user-1"
    user.role = role
    return user

@pytest.fixture
def mock_db():
    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db
    yield db
    app.dependency_overrides.clear()
    
    
@pytest.fixture
def client():
    return TestClient(app)

class TestNearbyResourcesRoute:
    def test_route_registered(self):
        matching = [r for r in app.routes if getattr(r, "path", None) == "/api/resources"]
        assert matching, "GET /api/resources is not registered"
        assert "GET" in matching[0].methods
        
    def test_requires_authentication(self, client, mock_db):
        res = client.get("/api/resources", params={"lat": -25.7461, "lng": 28.1881})
        assert res.status_code == 401
        
    def test_regular_user_forbidden(self, client, mock_db):
        from app.backend.src.dependencies import auth as auth_module
        
        app.dependency_overrides[auth_module.get_current_user] = lambda: fake_user(UserRole.user)
        res = client.get("/api/resources", params={"lat": -25.7461, "lng": 28.1881})
        assert res.status_code == 403
        
    def test_firefighter_allower(self, client, mock_db):
        from app.backend.src.dependencies import auth as auth_module
        
        app.dependency_overrides[auth_module.get_current_user] = lambda: fake_user(UserRole.firefighter)
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        res = client.get("/api/resources", params={"lat": -25.7461, "lng": 28.1881})
        assert res.status_code == 200, res.text
        assert res.json() == {"data": [], "total": 0}
        
    def test_admin_allowed(self, client, mock_db):
        from app.backend.src.dependencies import auth as auth_module
        
        app.dependency_overrides[auth_module.get_current_user] = lambda: fake_user(UserRole.admin)
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        res = client.get("/api/resources", params={"lat": -25.7461, "lng": 28.1881})
        assert res.status_code == 200, res.text
        
    def test_missing_lat_lng_is_422(self, client, mock_db):
        from app.backend.src.dependencies import auth as auth_modeule
        
        app.dependency_overrides[auth_modeule.get_current_user] = lambda: fake_user(UserRole.admin)
        assert client.get("/api/resources").status_code == 422
        assert client.get("/api/resources", params={"lat": -25.7461}).status_code == 422
        
    def test_radius_km_must_be_positive(self, client, mock_db):
        from app.backend.src.dependencies import auth as auth_module
        
        app.dependency_overrides[auth_module.get_current_user] = lambda: fake_user(UserRole.admin)
        res = client.get("/api/resources", params={"lat": -25.7461, "lng": 28.1881, "radius_km": 0})
        assert res.status_code == 422