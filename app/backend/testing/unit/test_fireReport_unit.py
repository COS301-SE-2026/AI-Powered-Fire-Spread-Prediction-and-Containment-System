# import pytest
# from datetime import datetime
# from fastapi.testclient import TestClient
# from unittest.mock import patch, MagicMock

# from main import app
# from db import get_db

# valid_payload = {
#     "lat": -33.9249,
#     "lng": 18.4241,
#     "location_text": "5th Ave and Pine St",
#     "description": "Bush fire near treeline",
#     "image_url": "https://example.com/fire.jpg",
#     "boundary_radius": 5.0
# }

# #test db
# #fixture shared that any test can request
# @pytest.fixture
# def mock_db():
#     db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: db
#     yield db
#     app.dependency_overrides.clear()

# #when client is called in tests this function gets called
# #creates fake HTTP client wired directly to FASTAPI for calling endpoints
# @pytest.fixture
# def client():
#     return TestClient(app)

# @pytest.fixture
# def mock_report():
#     report = MagicMock()
#     report.reference_number = f"FR-{datetime.now().year}-ABC123"
#     report.user_id = "usr_01"
#     report.id = "mock_123"
#     report.location_text = "5th Ave and Pine St"
#     report.description = valid_payload["description"]
#     report.boundary_radius = valid_payload["boundary_radius"]
#     report.image_url = valid_payload["image_url"]
#     report.status = "received"
#     report.status_index = 0
#     report.submitted_at = datetime(2025, 1, 1, 12, 0, 0)
#     return report

# ###test endpoint get_fire_reports
# #mock_db.query().all() returns []
# def test_empty_reports(client, mock_db):
#     mock_db.query.return_value.all.return_value = []
#     response = client.get("/api/guests/reported-fires")
#     assert response.status_code == 200 #success response
#     assert response.json() == []

# def test_return_report(client, mock_db, mock_report):
#     mock_db.query.return_value.all.return_value = [ (mock_report, valid_payload["lat"], valid_payload["lng"]) ]
#     response = client.get("/api/guests/reported-fires")
#     assert response.status_code == 200
#     report = response.json()[0]
#     assert report["reference_number"] == mock_report.reference_number
#     assert report["lat"] == pytest.approx(valid_payload["lat"])
#     assert report["lng"] == pytest.approx(valid_payload["lng"])
#     assert report["location_text"] == valid_payload["location_text"]
#     assert report["status"] == "received"

# def test_get_lat_lng(client, mock_db, mock_report):
#     mock_db.query.return_value.all.return_value = [(mock_report, -33.9249, 18.4241)]
#     response = client.get("/api/guests/reported-fires")
#     report = response.json()[0]
#     assert report["lat"] == pytest.approx(-33.9249)
#     assert report["lng"] == pytest.approx(18.4241)

# def test_multiple_returns(client, mock_db, mock_report):
#     mock_report_2 = MagicMock()
#     mock_report_2.reference_number = f"FR-{datetime.now().year}-BBB222"
#     mock_report_2.user_id = "usr_01"
#     mock_report_2.location_text = "5th Ave and Pine St"
#     mock_report_2.description = valid_payload["description"]
#     mock_report_2.boundary_radius = valid_payload["boundary_radius"]
#     mock_report_2.id = "mock_id_124"
#     mock_report_2.image_url = valid_payload["image_url"]
#     mock_report_2.status = "received"
#     mock_report_2.status_index = 0
#     mock_report_2.submitted_at = datetime(2025, 1, 2, 12, 0, 0)

#     mock_db.query.return_value.all.return_value = [ (mock_report, valid_payload["lat"], valid_payload["lng"]), (mock_report_2, -33.9249, 18.4241) ]
#     response = client.get("/api/guests/reported-fires")
#     assert response.status_code == 200
#     assert len(response.json()) == 2
#     assert response.json()[0]["reference_number"] == mock_report.reference_number
#     assert response.json()[1]["reference_number"] == mock_report_2.reference_number

# ###create_fire_report endpoint
# # returns 200
# def test_create_report(client, mock_db, mock_report):
#     with patch("services.users.fire_report.FireReports") as MockModel:
#         MockModel.return_value = mock_report
#         response = client.post("/api/guests/reported-fires", json=valid_payload)
#     assert response.status_code == 200

# #test reference number format
# def test_ref_format(client, mock_db, mock_report):
#     with patch("services.users.fire_report.FireReports") as MockModel:
#         MockModel.return_value = mock_report
#         response = client.post("/api/guests/reported-fires", json=valid_payload)

# #     ref = response.json()["reference_number"]
# #     year = datetime.now().year
# #     assert re.match(rf"FR-{year}-[A-F0-9]{{6}}", ref)

# #test status
# def test_status(client, mock_db, mock_report):
#     with patch("services.users.fire_report.FireReports") as MockModel:
#         MockModel.return_value = mock_report
#         response = client.post("/api/guests/reported-fires", json=valid_payload)

#     assert response.json()["status"] == "received"
#     assert response.json()["status_index"] == 0

# #test lat lng return
# def test_post_lat_lng(client, mock_db, mock_report):
#     with patch("services.users.fire_report.FireReports") as MockModel:
#         MockModel.return_value = mock_report
#         response = client.post("/api/guests/reported-fires", json=valid_payload)

#     assert response.json()["lat"] == pytest.approx(valid_payload["lat"])
#     assert response.json()["lng"] == pytest.approx(valid_payload["lng"])
