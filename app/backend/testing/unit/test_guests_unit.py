#we should add more tests as the valid ranges for fields become apparent throughout this project, should be fine for now.
import pytest
from pydantic import ValidationError #for explicit type checking, considering python doesn't do it for some reason
from datetime import datetime, timezone

from app.backend.src.models.reported_fires import FireReports
from app.backend.src.schemas.fire_report import FireReportCreate
from app.backend.src.enums.report_status import ReportStatus

#testing so that the correct data is sent to mapbox to display the fires
#the guest page map needs to get fire report data that is correctly structured.
class TestFireReportSchemaValidation:
    #helper for data values
    def _valid_payload(self, **overrides) -> dict:
        base = {
            "lat": 28.2435,
            "lng": -25.7480,
            "location_text": "LC de Villiers Sports Grounds, Hatfield",
            "description": "Brush fire starting near the northern fence along the road.",
            "boundary_radius": 0.5,
        }
        base.update(overrides)
        return base

    def test_lat_out_of_range_rejected(self):
        with pytest.raises(ValidationError):
            FireReportCreate(**self._valid_payload(lat=95))

    def test_boundary_radius_must_be_positive(self):
        with pytest.raises(ValidationError):
            FireReportCreate(**self._valid_payload(boundary_radius=0))

    def test_missing_required_field_causes_validation_error(self):
        payload = self._valid_payload()
        del payload["lat"]
        with pytest.raises(ValidationError):
            FireReportCreate(**payload)
