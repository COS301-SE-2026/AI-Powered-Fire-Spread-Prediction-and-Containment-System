import pytest
from models.reported_fires import FireReports
from datetime import datetime, timezone
from geoalchemy2.elements import WKTElement
from enums.report_status import ReportStatus

#helper function that loads the mock data into test db
def mock_fireReport(db):
    mock_report = FireReports(
        id="fr_test_01",
        reference_number="FR-2026-AABBCC",
        user_id=None,
        location_text="Hatfield, Pretoria",
        description="Test fire near campus",
        image_url="https://example.com/fire.jpg",
        location_geom=WKTElement("POINT(28.2293 -25.7479)", srid=4326),
        boundary_radius=2.0,
        status=ReportStatus.received,
        status_index=0,
        submitted_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(mock_report)
    db.commit()
    return mock_report

#test if nothing in db then endpoint returns HTTP 200 OK
def test_get_report_empty(client):
    response = client.get("/api/users/reported-fires")
    
    assert response.status_code == 200, (
        f"Expect 200 OK when DB is empty, returned {response.status_code}"
    )

    assert response.json() == [], (
        "Expect empty list when DB is empty, returned something in the list"
    )

#test if the report is in db then must appear in GET response
def test_get_reports(client, db):
    mock_fireReport(db)
    response = client.get("/api/users/reported-fires")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list), "must return list"
    assert len(data) >= 1, "must return atleast 1 report"

    refnums = []
    for r in response.json():
        refnums.append(r["reference_number"])
    assert "FR-2026-AABBCC" in refnums, " report not found in get response"

