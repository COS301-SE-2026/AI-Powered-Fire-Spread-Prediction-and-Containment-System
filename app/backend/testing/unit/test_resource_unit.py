from datetime import date, datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.backend.db import get_db
from app.backend.main import app
from app.backend.src.dependencies.auth import get_current_user
from app.backend.src.enums.resource import (
    CapacityUnit,
    ResourceStatus,
    ResourceType,
    capacity_unit_for,
)
from app.backend.src.enums.user_role import UserRole
from app.backend.src.models.water_resource import WaterResource
from app.backend.src.schemas.resource import ResourceCreate

VALID = {
    "resource": "water_tank",
    "otherResource": "",
    "otherCapacity": "",
    "capacity": 5000,
    "capacityUnit": "liters",
    "availableFrom": "2026-09-20",
    "availableUntil": "",
    "location": "Farmn on Old Warmbaths Rd, Pretoria North",
    "externalPin": {"lat": -25.7461, "lng": 28.1881},
    "name": "Pieter van der Merwe",
    "contact": "082 456 1234",
}

def payload(**overrides):
    return {**VALID, **overrides}

# Test schema
class TestResourceCreateSchema:
    def test_accepts_frontend_payload(self):
        r = ResourceCreate.model_validate(VALID)
        assert r.resource == ResourceType.water_tank
        assert r.available_from == date(2026, 9, 20)
        assert r.available_until is None
        assert r.external_pin.lat == -25.7461
        
    def test_missing_available_from_defaults_to_today(self):
        data = payload(availableFrom="")
        r = ResourceCreate.model_validate(data)
        assert r.available_from == datetime.now(timezone.utc).date()
        
    def test_text_fields_are_stripped(self):
        r = ResourceCreate.model_validate(payload(name=" Sarah Botha ", contact="0839982211"))
        assert r.name == "Sarah Botha"
        assert r.contact == "0839982211"
        
    @pytest.mark.parametrize("name", ["", " ", "12345", "ab"])
    def test_rejects_bad_names(self, name):
        with pytest.raises(ValidationError):
            ResourceCreate.model_validate(payload(name=name))
            
    @pytest.mark.parametrize("contact", ["", "12345", "0824561", "082 456 1234 5", "0000000000", "1111111111", "abc"])
    def test_rejects_bad_contacts(self, contact):
        with pytest.raises(ValidationError):
            ResourceCreate.model_validate(payload(contact=contact))
            
    @pytest.mark.parametrize("contact", ["082 456 1234", "0824561234", "+27 82 456 1234", "27824561234"])
    def test_accepts_south_african_numbers(self, contact):
        assert ResourceCreate.model_validate(payload(contact=contact)).contact == contact
        
    @pytest.mark.parametrize("capacity", [0, -1, float("nan")])
    def test_rejects_non_positive_capacity(self, capacity):
        with pytest.raises(ValidationError):
            ResourceCreate.model_validate(payload(capacity=capacity))
            
    def test_rejects_capacity_over_limit(self):
        with pytest.raises(ValidationError):
            ResourceCreate.model_validate(payload(capacity=150_001))
        assert ResourceCreate.model_validate(payload(capacity=150_000)).capacity == 150_000
        
    def test_crew_limits(self):
        assert ResourceCreate.model_validate(payload(resource="crew", capacity=8)).capacity == 8
        with pytest.raises(ValidationError):
            ResourceCreate.model_validate(payload(resource="crew", capacity=1001))
        with pytest.raises(ValidationError):
            ResourceCreate.model_validate(payload(resource="crew", capacity=2.5))
            
    def test_other_requires_description(self):
        with pytest.raises(ValidationError):
            ResourceCreate.model_validate(payload(resource="other", otherResource=" "))
        r = ResourceCreate.model_validate(
            payload(resource="other", otherResource="Diesel Generator", otherCapacity="L of fuel")
        )
        assert r.other_resource == "Diesel Generator"
        assert r.other_capacity == "L of fuel"
        
    def test_free_text_cleared_when_not_other(self):
        r = ResourceCreate.model_validate(payload(otherResource="leftover", otherCapacity="boxes"))
        assert r.other_resource == ""
        assert r.other_capacity == ""
        
    def test_rejects_unknown_resource_type(self):
        with pytest.raises(ValidationError):
            ResourceCreate.model_validate(payload(resource="helicopter"))
            
    @pytest.mark.parametrize(
        "pin",
        [{"lat": 0, "lng": 0}, {"lat": 91, "lng": 10}, {"lat": 10, "lng": 181}, None],
    )
    def test_rejects_bad_pin(self, pin):
        with pytest.raises(ValidationError):
            ResourceCreate.model_validate(payload(externalPin=pin))
            
    def test_until_before_from_rejected_same_day_allowed(self):
        with pytest.raises(ValidationError):
            ResourceCreate.model_validate(payload(availableFrom="2026-09-20", availableUntil="2026-09-19"))
        r = ResourceCreate.model_validate(payload(availableFrom="2026-09-20", availableUntil="2026-09-20"))
        assert r.available_until == date(2026, 9, 20)
        
    def test_short_location_rejected(self):
        with pytest.raises(ValidationError):
            ResourceCreate.model_validate(payload(location=" a "))
            
    def test_snake_case_also_accepted(self):
        data = {
            "resource": "dam",
            "capacity": 100,
            "location": "Somewhere",
            "external_pin": {"lat": -25.0, "lng": 28.0},
            "name": "Big Dam",
            "contact": "0821234567",
        }
        assert ResourceCreate.model_validate(data).resource == ResourceType.dam
        
class TestCapacityUnit:
    @pytest.mark.parametrize(
        "rtype,unit",
        [
            (ResourceType.water_tank, CapacityUnit.liters),
            (ResourceType.borehole, CapacityUnit.liters),
            (ResourceType.trailer, CapacityUnit.liters),
            (ResourceType.dam, CapacityUnit.liters),
            (ResourceType.aircraft, CapacityUnit.liters),
            (ResourceType.crew, CapacityUnit.members),
            (ResourceType.other, CapacityUnit.other),
        ],
    )
    def test_unit_derived_from_type(self, rtype, unit):
        assert capacity_unit_for(rtype) == unit
        
# Test route
def fake_user(role=UserRole.user):
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
def as_user(mock_db):
    app.dependency_overrides[get_current_user] = lambda: fake_user()
    yield
    
@pytest.fixture
def client():
    return TestClient(app)

class TestRegisterResourceRoute:
    def test_route_registered(self):
        matching = [r for r in app.routes if getattr(r, "path", None) == "/api/users/resources"]
        methods = set().union(*(r.methods for r in matching))
        assert {"GET", "POST"} <= methods
        
    def test_requires_authentication(self, client, mock_db):
        res = client.post("/api/users/resources", json=VALID)
        assert res.status_code == 401
        mock_db.add.assert_not_called()
        
    def test_creates_resource(self, client, mock_db, as_user):
        res = client.post("/api/users/resources", json=VALID)
        
        assert res.status_code == 201, res.text
        saved: WaterResource = mock_db.add.call_args[0][0]
        assert saved.user_id == "user-1"
        assert saved.resource_type == ResourceType.water_tank
        assert saved.capacity_unit == CapacityUnit.liters
        assert saved.status == ResourceStatus.available
        assert saved.available_until is None
        assert saved.location_geom == "SRID=4326;POINT(28.1881 -25.7461)"
        mock_db.commit.assert_called_once()
        
        body = res.json()
        assert body["resource"] == "water_tank"
        assert body["capacityUnit"] == "liters"
        assert body["status"] == "available"
        assert body["externalPin"] == {"lat": -25.7461, "lng": 28.1881}
        assert body["availableFrom"] == "2026-09-20"
        assert body["availableUntil"] is None
        assert body["otherResource"] == ""
        assert body["id"] == saved.id
        
    def test_client_capacity_unit_is_ignored(self, client, mock_db, as_user):
        res = client.post("/api/users/resources", json=payload(resource="crew", capacity=6, capacityUnit="liters"))
        assert res.status_code == 201, res.text
        assert res.json()["capacityUnit"] == "members"
        
    def test_invalid_payload_is_422_and_nothing_saved(self, client, mock_db, as_user):
        res = client.post("/api/users/resources", json=payload(name="12345"))
        assert res.status_code == 422
        mock_db.add.assert_not_called()
        
    def test_extra_fields_from_frontend_are_ignored(self, client, mock_db, as_user):
        res = client.post("/api/users/resources", json=payload(fireRef="FR-2026-ABC123"))
        assert res.status_code == 201, res.text
        assert "fireRef" not in res.json()
        
    def test_list_limit_validated(self, client, mock_db, as_user):
        assert client.get("/api/users/resources?limit=0").status_code == 422
        assert client.get("/api/users/resources?limit=101").status_code == 422
        assert client.get("/api/users/resources?offset=-1").status_code == 422
        
    def test_list_requires_authentication(self, client, mock_db):
        assert client.get("/api/users/resources").status_code == 401
