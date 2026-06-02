import pytest
from geoalchemy2.elements import WKTElement
from models import FireReport, ReportStatus

client = TestClient(app)

def test_guest_fire_map_integration(client, db):
    """Validate data retrieval for guest live map view"""

    #mock record into test db
    mock_fire = FireReportModel(
        reference_number="FR-2026-100",
        user_id="usr_01",
        location_text="Place 1"
        description="Fake fire"
        location_geom=WKTElement("POINT(28.2293 -25.7479)", srid=4326),
        boundary_radius_km=2,
        status=ReportStatus.verified,
        status_index=2
    )

    db.add(mock_fire)
    db.commit

    response = client.get("api/reports/public")

    assert response.status_code == 200, "Since it is public unautherised shouldn't be returned"

    data = response.json()
    assert isinstance(data, list), "Expect a list of fire reports"
    assert len(data) >= 1, "At least one active fire"

    guest_fire = next((item ))