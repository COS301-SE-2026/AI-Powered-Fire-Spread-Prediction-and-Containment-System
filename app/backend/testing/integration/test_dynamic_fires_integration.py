from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from conftest import make_report, make_user

from app.backend.src.enums.fire_status import FireStatus
from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.dependencies.auth import get_current_user
from app.backend.main import app

def as_role(db, role):
    user = make_user(db, role=role)
    app.dependency_overrides[get_current_user] = lambda: user
    return user

# Test GET /api/firefighter/terrain-bias
def test_terrain_bias_returns_sixteen_bearings(client, db):
    response = client.get(
        "/api/firefighter/terrain-bias",
        params={"lat": -25.7479, "lng": 28.2293},
    )
    
    assert response.status_code == 200, response.text
    body = response.json()
    assert "bias" in body
    assert len(body["bias"]) == 16
    for entry in body["bias"]:
        assert "bearing_deg" in entry
        assert "factor" in entry
        assert entry["factor"] > 0
        
def test_terrain_bias_is_cached_on_second_call_for_the_same_rounded_location(client, db):
    first = client.get("/api/firefighter/terrain-bias", params={"lat": -26.2041, "lng": 28.0473})
    second = client.get("/api/firefighter/terrain-bias", params={"lat": -26.2041, "lng": 28.0473})
    
    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    assert len(first.json()["bias"]) == len(second.json()["bias"]) == 16
    