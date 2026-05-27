import pytest
import re
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from main import app 
from db import get_db

valid_payload = {
    "location": "5th Ave and Pine St",
    "description": "Bush fire neat treeline",
    "lat": 47.608013,
    "lng": -122.335167,
    "boundary_radius_km": 2.0,
    "user_id": None
}

#test db
#fixture shared that any test can request
@pytest.fixture
def mock_db():
    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db
    yield db
    app.dependency_overrides.clear()

#when client is called in tests this function gets called 
#creates fake HTTP client wired directly to FASTAPI for calling endpoints
@pytest.fixture
def client():
    return TestClient(app)

###test endpoint get_fire_reports
#mock_db.query().all() returns [] 
def test_empty_reports(client, mock_db):
    mock_db.query.return_value.all.return_value = []
    response = client.get("/api/reports")
    assert response.status_code == 200 #success response 
    assert response.json() == []

def test_return_report(client, mock_db):
    mock_report = MagicMock()
    #sets all attributes endpoint reads
    mock_report.reference_number = "FR-2025-ABC123"
    mock_report.user_id = None
    mock_report.location_text = "5th Ave and Pine St"
    mock_report.description = "Brush fire near treeline"
    mock_report.boundary_radius_km = 2.0
    mock_report.status.value = "received"
    mock_report.status_index = 0
    mock_report.submitted_at = datetime(2025, 1, 1, 12, 0, 0)
    
    mock_db.query.return_value.all.return_value = [ (mock_report, 47.608013, -122.335167) ]

    response = client.get("/api/reports")
    assert response.status_code == 200 

    report = response.json()[0]
    assert report["reference_number"] == "FR-2025-ABC123"
    assert report["lat"] == 47.608013
    assert report["lng"] == -122.335167
    assert report["location"] == "5th Ave and Pine St"
    assert report["status"] == "received"

def test_get_lat_lng(client, mock_db):
    mock_report = MagicMock()
    mock_report.reference_number = "FR-2025-ABC123"
    mock_report.user_id = None                        
    mock_report.location_text = "5th Ave"             
    mock_report.description = "Brush fire"            
    mock_report.boundary_radius_km = 2.0              
    mock_report.status.value = "received"
    mock_report.status_index = 0                     
    mock_report.submitted_at = datetime(2025, 1, 1, 0, 0)

    mock_db.query.return_value.all.return_value = [ (mock_report, -33.9249, 18.4241) ]

    response = client.get("/api/reports")
    report = response.json()[0]
    assert report["lat"] == -33.9249
    assert report["lng"] == 18.4241

def test_multiple_returns(client, mock_db):
    mock_report_1 = MagicMock()
    mock_report_1.reference_number = "FR-2025-AAA111"
    mock_report_1.user_id = None
    mock_report_1.location_text = "5th Ave"
    mock_report_1.description = "Brush fire"
    mock_report_1.boundary_radius_km = 2.0
    mock_report_1.status.value = "received"
    mock_report_1.status_index = 0
    mock_report_1.submitted_at = datetime(2025, 1, 1, 12, 0, 0)

    mock_report_2 = MagicMock()
    mock_report_2.reference_number = "FR-2025-BBB222"
    mock_report_2.user_id = None
    mock_report_2.location_text = "Elm Street"
    mock_report_2.description = "Forest fire"
    mock_report_2.boundary_radius_km = 5.0
    mock_report_2.status.value = "received"
    mock_report_2.status_index = 0
    mock_report_2.submitted_at = datetime(2025, 1, 2, 12, 0, 0)
    
    mock_db.query.return_value.all.return_value = [ (mock_report_1, 47.608013, -122.335167), (mock_report_2, -33.9249, 18.4241) ]

    response = client.get("/api/reports")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["reference_number"] == "FR-2025-AAA111"
    assert response.json()[1]["reference_number"] == "FR-2025-BBB222"

###create_fire_report endpoint
# returns 200
def test_create_report(client, mock_db):
    mock_report = MagicMock()
    mock_report.reference_number = "FR-2025-ABC123"
    mock_report.user_id = None
    mock_report.location_text = "5th Ave and Pine St"
    mock_report.description = "Brush fire near treeline"
    mock_report.boundary_radius_km = 2.0
    mock_report.status.value = "received"
    mock_report.status_index = 0
    mock_report.submitted_at = datetime(2025, 1, 1, 12, 0, 0)

    with patch("report.fireReports.FireReportModel") as MockModel:
        MockModel.return_value = mock_report 
        response = client.post("/api/reports", json=valid_payload)
    
    assert response.status_code == 200

#test reference number format
def test_ref_format(client, mock_db):
    mock_report = MagicMock()
    mock_report.reference_number = f"FR-{datetime.now().year}-ABC123"
    mock_report.user_id = None
    mock_report.location_text = "5th Ave and Pine St"
    mock_report.description = "Brush fire near treeline"
    mock_report.boundary_radius_km = 2.0
    mock_report.status.value = "received"
    mock_report.status_index = 0
    mock_report.submitted_at = datetime(2025, 1, 1, 12, 0, 0)

    with patch("report.fireReports.FireReportModel") as MockModel:
        MockModel.return_value = mock_report
        response = client.post("/api/reports", json=valid_payload)

    ref = response.json()["reference_number"]
    year = datetime.now().year
    assert re.match(rf"FR-{year}-[A-F0-9]{{6}}", ref)

#test status 
def test_status(client, mock_db):
    mock_report = MagicMock()
    mock_report.user_id = None
    mock_report.reference_number = "FR-2025-ABC123"
    mock_report.location_text = "5th Ave and Pine St"
    mock_report.description = "Brush fire near treeline"
    mock_report.boundary_radius_km = 2.0
    mock_report.status.value = "received"
    mock_report.status_index = 0
    mock_report.submitted_at = datetime(2025, 1, 1, 12, 0, 0)

    with patch("report.fireReports.FireReportModel") as MockModel:
        MockModel.return_value = mock_report
        response = client.post("/api/reports", json=valid_payload)
    
    assert response.json()["status"] == "received"
    assert response.json()["status_index"] == 0

#test lat lng return 
def test_post_lat_lng(client, mock_db):
    mock_report = MagicMock()
    mock_report.user_id = None
    mock_report.reference_number = "FR-2025-ABC123"
    mock_report.location_text = "5th Ave and Pine St"
    mock_report.description = "Brush fire near treeline"
    mock_report.boundary_radius_km = 2.0
    mock_report.status.value = "received"
    mock_report.status_index = 0
    mock_report.submitted_at = datetime(2025, 1, 1, 12, 0, 0)

    with patch("report.fireReports.FireReportModel") as MockModel:
        MockModel.return_value = mock_report
        response = client.post("/api/reports", json=valid_payload)
    
    assert response.json()["lat"] == valid_payload["lat"]
    assert response.json()["lng"] == valid_payload["lng"]






        
