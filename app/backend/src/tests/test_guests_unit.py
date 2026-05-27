import pytest
import pydantic import ValidationError #for explicit type checking, considering python doesn't do it for some reason
from datetime import datetime, timezone

from models import FireReport, FireReportCreate, FireReportModel, ReportStatus

#testing so that the correct data is sent to mapbox to display the fires
def test_valid_fire_report_schema():
    "Model successfully validates and parses the correct date that is required for the public incident map, data is also typechecked."
    valid_data = {
        "reference_number": "FR-2026-001",
        "user_id": "usr_01", 
        "location": "LC de Villiers Sports Grounds, Hatfield",
        "description": "Brush fire starting near the northern fence along the road.",
        "lat": 28.2435,
        "lng": -25.7480,
        "boundary_radius_km": 0.5,
        "status": ReportStatus.verified,
        "status_index": 2,
        #need to change to valid time
        "submitted_at": "0000-00-00T00:00:00Z", 
    }

    #takes key value pairs out of dictionary into function (the asterisks)
    report = FireReport(**valid_data)

    assert report.reference_number == "FR-2026-001"
    assert report.lat == 28.2435
    #need to add more. Just tired now

#also need to add security test for guest