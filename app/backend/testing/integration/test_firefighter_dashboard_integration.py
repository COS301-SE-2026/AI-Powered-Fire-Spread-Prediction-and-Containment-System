import pytest
from conftest import make_report
from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.services.firefighter import firefighter_dashboard

FAKE_CONDS = {
    "temperature": 24.0,
    "humidity": 30.0,
    "wind_speed": 12.0,
    "wind_direction": 90,
    "fdi": 62.0,
    "fdi_band": "DANGEROUS",
    "fdi_color": "yellow",
}

@pytest.fixture
def stub_fuel_conds(monkeypatch):
    monkeypatch.setattr(
        firefighter_dashboard, "get_fuel_conditions", lambda lat, lng: FAKE_CONDS
    )

# draw a line test for a line within 5km
def test_log_containment_line_2km(client, db):
    fire = make_report(db, status=ReportStatus.verified)

    response = client.post(
        "/api/firefighter/containment-line",
        json={"wkt": "LINESTRING(28.2293 -25.7579, 28.2350 -25.7600)"},
    )

    assert (
        response.status_code == 200
    ), f"Expected 200 if containment line within 2km of reported fire. Response code: {response.status_code}"


# draw a line test for a line outside 5km
def test_log_containment_line_5km(client, db):
    fire = make_report(db, lat=-25.700, lng=28.2293, status=ReportStatus.verified)

    response = client.post(
        "/api/firefighter/containment-line",
        json={"wkt": "LINESTRING(28.2293 -25.7929, 28.2350 -25.7950)"},
    )

    assert (
        response.status_code == 400
    ), f"Expected 400 if containment line outside 2km of reported fire. Response code: {response.status_code}"


# testing for nearby fires and weather api response with default coords success
def test_nearby_weather_success(client, db, stub_fuel_conds):
    response = client.get(
        "/api/firefighter/dashboard",
        params={"lat": -25.7479, "lng": 28.2293, "radius_km": 20},
    )

    assert response.status_code == 200, response.text

    env = response.json()["environment_variables"]
    assert env["fire_danger"] == "DANGEROUS"
    assert env["fdi"] == 62.0
    assert env["fdi_color"] == "yellow"
    assert env["wind"] == 12.0
    assert env["wind_dir"] == 90

def test_weather_failure_returns_404(client, db, monkeypatch):
    def fail(lat, lng):
        raise ValueError("Failed to fetch fuel conditions, timeout")

    monkeypatch.setattr(firefighter_dashboard, "get_fuel_conditions", fail)

    response = client.get(
        "/api/firefighter/dashboard",
        params={"lat": -25.7479, "lng": 28.2293}
    )

    assert response.status_code == 404