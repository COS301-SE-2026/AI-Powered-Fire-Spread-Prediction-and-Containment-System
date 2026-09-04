import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.backend.main import app
from app.backend.db import get_db
from app.backend.src.enums.report_status import ReportStatus

valid_payload = {
    "lat": -33.9249,
    "lng": 18.4241,
    "location_text": "5th Ave and Pine St",
    "description": "Bush fire near treeline",
    "image_url": "https://example.com/fire.jpg",
    "boundary_radius": 5.0,
}


# test db
# fixture shared that any test can request
@pytest.fixture
def mock_db():
    db = MagicMock()
    def _fake_refresh(obj):
        if getattr(obj, "submitted_at", None) is None:
            obj.submitted_at = datetime.now(timezone.utc)
 
    db.refresh.side_effect = _fake_refresh
 
    app.dependency_overrides[get_db] = lambda: db
    yield db
    app.dependency_overrides.clear()


# when client is called in tests this function gets called
# creates fake HTTP client wired directly to FASTAPI for calling endpoints
@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_report_dict():
    return {
        "id": "mock_123",
        "reference_number": f"FR-{datetime.now().year}-ABC123",
        "location_text": valid_payload["location_text"],
        "boundary_radius": float(valid_payload["boundary_radius"]),
        "user_id": "usr_01",
        "description": valid_payload["description"],
        "image_url": valid_payload["image_url"],
        "lat": valid_payload["lat"],
        "lng": valid_payload["lng"],
        "status": ReportStatus.received,
        "submitted_at": datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        "size": 78.5,
        "priority": "normal",
        "system_verified": False,
        "verification_notes": None,
        "reporter_name": "Anonymous",
    }


###test endpoint get_fire_reports
# mock_db.query().all() returns []
def test_empty_reports(client, mock_db):
    with patch(
        "app.backend.src.services.users.fire_report.get_fire_reports",
        return_value=[],
    ):
        response = client.get("/api/guests/reported-fires")
        assert response.status_code == 200  # success response
        assert response.json() == []


def test_return_report(client, mock_db, sample_report_dict):
    with patch(
        "app.backend.src.services.users.fire_report.get_fire_reports",
        return_value=[sample_report_dict],
    ):
        response = client.get("/api/guests/reported-fires")
        assert response.status_code == 200
        report = response.json()[0]
        assert report["reference_number"] == sample_report_dict["reference_number"]
        assert report["lat"] == pytest.approx(valid_payload["lat"])
        assert report["lng"] == pytest.approx(valid_payload["lng"])
        assert report["location_text"] == valid_payload["location_text"]
        assert report["status"] == "received"


def test_get_lat_lng(client, mock_db, sample_report_dict):
    sample_report_dict["lat"] = -33.9249
    sample_report_dict["lng"] = 18.4241

    with patch(
        "app.backend.src.services.users.fire_report.get_fire_reports",
        return_value=[sample_report_dict],
    ):

        response = client.get("/api/guests/reported-fires")
        report = response.json()[0]
        assert report["lat"] == pytest.approx(-33.9249)
        assert report["lng"] == pytest.approx(18.4241)


def test_multiple_returns(client, mock_db, sample_report_dict):
    second_report = dict(sample_report_dict)
    second_report["id"] = "mock_id_124"
    second_report["reference_number"] = f"FR-{datetime.now().year}-BBB222"

    with patch(
        "app.backend.src.services.users.fire_report.get_fire_reports",
        return_value=[sample_report_dict, second_report],
    ):

        response = client.get("/api/guests/reported-fires")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["reference_number"] == sample_report_dict["reference_number"] 
        assert data[1]["reference_number"] == second_report["reference_number"]


###create_fire_report endpoint
# returns 200
def test_create_report(client, mock_db, sample_report_dict):
    with patch(
        "app.backend.src.services.users.fire_report.get_fire_reports",
        return_value=sample_report_dict,
    ):
        response = client.post("/api/guests/reported-fires", json=valid_payload)
        assert response.status_code == 200


# test reference number format
def test_ref_format(client, mock_db, sample_report_dict):
    with patch(
        "app.backend.src.services.users.fire_report.get_fire_reports",
        return_value=sample_report_dict,
    ):
        response = client.post("/api/guests/reported-fires", json=valid_payload)
        assert response.status_code == 200
        assert "reference_number" in response.json()


#     ref = response.json()["reference_number"]
#     year = datetime.now().year
#     assert re.match(rf"FR-{year}-[A-F0-9]{{6}}", ref)


# test status
# def test_status(client, mock_db, sample_report_dict):
#    with patch(
#         "app.backend.src.services.users.fire_report.get_fire_reports",
#         return_value=sample_report_dict,
#     ):
#     response = client.post("/api/guests/reported-fires", json=valid_payload)
#     assert response.status_code == 200
#     assert response.json()["status"] == "received"


# test lat lng return
def test_post_lat_lng(client, mock_db, sample_report_dict):
    with patch(
        "app.backend.src.services.users.fire_report.get_fire_reports",
        return_value=sample_report_dict,
    ):
        response = client.post("/api/guests/reported-fires", json=valid_payload)
        assert response.status_code == 200
        assert response.json()["lat"] == pytest.approx(valid_payload["lat"])
        assert response.json()["lng"] == pytest.approx(valid_payload["lng"])
