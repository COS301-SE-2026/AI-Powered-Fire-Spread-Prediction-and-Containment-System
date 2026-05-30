#we should add more tests as the valid ranges for fields become apparent throughout this project, should be fine for now.
import pytest
from pydantic import ValidationError #for explicit type checking, considering python doesn't do it for some reason
from datetime import datetime, timezone

from models import FireReport, FireReportCreate, FireReportModel, ReportStatus

#testing so that the correct data is sent to mapbox to display the fires
#the guest page map needs to get fire report data that is correctly structured.
class TestFireReportSchemaValidation:
    #helper for data values
    def _valid_payload(self, **overrides) -> dict:
        """The valid base payload. Each test can override the fields as needed."""
        base = {
            "reference_number": "FR-2026-001",
            "user_id": "usr_01", 
            "location": "LC de Villiers Sports Grounds, Hatfield",
            "description": "Brush fire starting near the northern fence along the road.",
            "lng": -25.7480,
            "lat": 28.2435,
            "boundary_radius_km": 0.5,
            "status": ReportStatus.verified,
            "status_index": 2,
            #need to change to valid time
            "submitted_at": "2026-05-22T10:00:00Z", 
        }
        base.update(overrides)
        return base

    def test_valid_fire_report_schema(self):
        """tests if the fire report follows the valid data schema"""

        report = FireReport(**self._valid_payload())

        assert report.reference_number == "FR-2026-001"
        assert report.user_id == "usr_01"
        assert report.lng == pytest.approx(-25.7480)
        assert report.lat == pytest.approx(28.2435)
        assert report.boundary_radius_km == pytest.approx(0.5)
        assert report.status == ReportStatus.verified
        assert report.status_index == 2

    def test_ref_nr_is_string(self):
        """test to check that the reference number is a string"""
        with pytest.raises((ValidationError, TypeError)):
            FireReport(**self._valid_payload(reference_number=20260001))

    def test_status_valid_enum(self):
        """test to check that the test status is a valid enum from the enum possibilities"""
        with pytest.raises(ValidationError):
            FireReport(**self._valid_payload(status="wrong_string_enum"))

    def test_all_statuses_accepted(self):
        """test to check that all the valid report statuses are accepted"""
        for status in ReportStatus:
            report = FireReport(**self._valid_payload(status=status))
            assert report.status == status

    def test_missing_required_field_causes_validation_error(self):
        """test to make sure that the payload isn't sent without required fields"""
        payload = self._valid_payload()
        del payload["lat"]
        with pytest.raises(ValidationError):
            FireReport(**payload)
