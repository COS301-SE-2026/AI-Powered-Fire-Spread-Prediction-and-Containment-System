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
        