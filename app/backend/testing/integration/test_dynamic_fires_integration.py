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
    
# Test GET /api/firefighter/reported-fires
def test_reported_fires_includes_fire_status_field(client, db):
    make_report(db, status=ReportStatus.verified, boundary_radius=0.3)
    
    response = client.get("/api/firefighter/reported-fires")
    
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert len(data) >= 1
    fire = data[0]
    assert "fire_status" in fire
    assert "containment_percent" in fire
    assert "merged_into_id" in fire
    assert "updated_at" in fire
    assert fire["fire_status"] == "active"
    
def test_merged_fire_is_excluded_from_growable_fires_by_reference(client, db):
    fire = make_report(db, status=ReportStatus.verified)
    other = make_report(db, status=ReportStatus.verified)
    fire.merged_into_id = other.id
    db.commit()
    
    response = client.get("/api/firefighter/reported-fires")
    data = response.json()["data"]
    merged_entry = next(f for f in data if f["id"] == fire.id)
    assert merged_entry["merged_into_id"] == other.id
    
def test_close_overlapping_fires_do_not_merge_before_debounce_elapses(client, db):
    now = datetime.now(timezone.utc)
    fire_a = make_report(db, lat=-25.75, lng=28.23, boundary_radius=5.0, status=ReportStatus.verified, submitted_at=now - timedelta(minutes=5))
    fire_b = make_report(db, lat=-25.75, lng=28.23, boundary_radius=5.0, status=ReportStatus.verified, submitted_at=now)
    
    client.get("/api/firefighter/reported-fires")
    
    db.refresh(fire_a)
    db.refresh(fire_b)
    assert fire_a.merged_into_id is None
    assert fire_b.merged_into_id is None
    
@patch("app.backend.src.services.firefighter.fire_merge.is_persistently_overlapping", return_vale=True)
def test_overlapping_fires_merge_once_debounce_is_satisfied(mock_debounce, client, db):
    now = datetime.now(timezone.utc)
    older = make_report(db, lat=-25.75, lng=28.23, boundary_radius=5.0, status=ReportStatus.verified, submitted_at=now - timedelta(hours=1))
    newer = make_report(db, lat=-25.75, lng=28.23, boundary_radius=5.0, status=ReportStatus.verified, submitted_at=now)
    
    response = client.get("/api/firefighter/reported-fires")
    assert response.status_code == 200, response.text
    
    db.refresh(older)
    db.refresh(newer)
    assert newer.merged_into_id == older.id
    assert older.merged_into_id is None