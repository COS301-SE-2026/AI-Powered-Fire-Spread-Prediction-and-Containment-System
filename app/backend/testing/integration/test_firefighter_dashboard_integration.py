from conftest import make_report
from app.backend.src.enums.report_status import ReportStatus


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
def test_nearby_weather_success(client, db):
    response = client.get(
        "/api/firefighter/dashboard",
        params={"lat": -25.7479, "lng": 28.2293, "radius_km": 20},
    )

    assert response.status_code == 200, {
        f"Expected response code is 200 if the nearby fires are found within radius_km. Response code: {response.status_code}"
    }
