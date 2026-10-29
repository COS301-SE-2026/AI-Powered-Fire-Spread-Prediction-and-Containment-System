import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
import httpx
import pytest

from app.backend.src.services.verification import rejection_checks
from app.backend.src.services.verification.rejection_checks import (
    LocationCheckUnavailable,
    get_report_coordinates,
    within_boundary,
    valid_location,
    on_land,
    valid_timestamp,
    duplicate_submission,
    required_fields_present,
    rejection_check,
)


class TestGetReportCoordinates:
    def test_location_geom_none_returns_none(self):
        report = MagicMock(location_geom=None)
        assert get_report_coordinates(report) is None

    def test_to_shape_exception_returns_none(self, monkeypatch):
        report = MagicMock(id=1, location_geom="CORRUPTED_GEOM")

        def raise_shape_error(_geom):
            raise ValueError("Corrupt geometry WKB")

        monkeypatch.setattr(rejection_checks, "to_shape", raise_shape_error)
        assert get_report_coordinates(report) is None

    def test_get_report_coordinates_success(self, monkeypatch):
        report = MagicMock(id=1, location_geom="VALID_GEOM")
        mock_point = MagicMock(x=18.4241, y=-33.9249)
        monkeypatch.setattr(rejection_checks, "to_shape", lambda _g: mock_point)

        coords = get_report_coordinates(report)
        assert coords == (-33.9249, 18.4241)


class TestBoundaryAndLocation:
    def test_valid_location(self):
        assert valid_location(0.0, 0.0) is False
        assert valid_location(-33.9249, 18.4241) is True

    def test_within_boundary_valid(self):
        assert within_boundary(-30.0, 25.0) is True

    def test_within_boundary_out_of_bounds(self):
        assert within_boundary(-35.5, 25.0) is False
        assert within_boundary(-21.0, 25.0) is False
        assert within_boundary(-30.0, 15.0) is False
        assert within_boundary(-30.0, 33.5) is False


class TestOnLand:
    def test_on_land_returns_true_when_no_water_features(self, monkeypatch):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"features": []}
        monkeypatch.setattr(httpx, "get", MagicMock(return_value=mock_resp))

        assert on_land(-33.9249, 18.4241) is True

    def test_on_land_returns_false_when_water_features_detected(self, monkeypatch):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"features": [{"id": 1, "layer": "water"}]}
        monkeypatch.setattr(httpx, "get", MagicMock(return_value=mock_resp))

        assert on_land(-33.9249, 18.4241) is False

    def test_on_land_http_error_raises_location_check_unavailable(self, monkeypatch):
        monkeypatch.setattr(
            httpx,
            "get",
            MagicMock(side_effect=httpx.HTTPError("Network failed")),
        )
        with pytest.raises(LocationCheckUnavailable, match="on_land check failed"):
            on_land(-33.9249, 18.4241)

    def test_on_land_json_decode_error_raises_location_check_unavailable(self, monkeypatch):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.side_effect = json.JSONDecodeError("Expecting value", "doc", 0)
        monkeypatch.setattr(httpx, "get", MagicMock(return_value=mock_resp))

        with pytest.raises(LocationCheckUnavailable, match="on_land check failed"):
            on_land(-33.9249, 18.4241)


class TestValidTimestamp:
    def test_valid_timestamp_naive_converts_to_utc(self):
        now_utc = datetime.now(timezone.utc)
        naive_recent = datetime(now_utc.year, now_utc.month, now_utc.day, now_utc.hour, now_utc.minute)
        assert valid_timestamp(naive_recent) is True

    def test_valid_timestamp_future_returns_false(self):
        future = datetime.now(timezone.utc) + timedelta(hours=2)
        assert valid_timestamp(future) is False

    def test_valid_timestamp_too_old_returns_false(self):
        old = datetime.now(timezone.utc) - timedelta(days=8)
        assert valid_timestamp(old) is False


class TestDuplicateSubmission:
    def test_duplicate_submission_anonymous_user_returns_false(self, monkeypatch):
        mock_point = MagicMock(wkt="POINT(18.4241 -33.9249)")
        monkeypatch.setattr(rejection_checks, "to_shape", lambda _g: mock_point)

        report = MagicMock(
            user_id=None,
            submitted_at=datetime.now(timezone.utc),
            location_geom="GEOM",
        )
        mock_session = MagicMock()
        assert duplicate_submission(report, mock_session) is False
        mock_session.execute.assert_not_called()

    def test_duplicate_submission_found_returns_true(self, monkeypatch):
        mock_point = MagicMock(wkt="POINT(18.4241 -33.9249)")
        monkeypatch.setattr(rejection_checks, "to_shape", lambda _g: mock_point)

        report = MagicMock(
            id=10,
            user_id="usr-123",
            submitted_at=datetime.now(timezone.utc),
            location_geom="GEOM",
        )
        mock_session = MagicMock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = 9

        assert duplicate_submission(report, mock_session) is True

    def test_duplicate_submission_none_found_returns_false(self, monkeypatch):
        mock_point = MagicMock(wkt="POINT(18.4241 -33.9249)")
        monkeypatch.setattr(rejection_checks, "to_shape", lambda _g: mock_point)

        report = MagicMock(
            id=10,
            user_id="usr-123",
            submitted_at=datetime.now(timezone.utc),
            location_geom="GEOM",
        )
        mock_session = MagicMock()
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        assert duplicate_submission(report, mock_session) is False


class TestRequiredFieldsPresent:
    def test_required_fields_present_success(self):
        report = MagicMock(
            location_geom="GEOM",
            submitted_at=datetime.now(timezone.utc),
            image_url="https://s3.example.com/photo.jpg",
        )
        assert required_fields_present(report) is True

    def test_required_fields_present_missing_or_empty(self):
        report_missing = MagicMock(
            location_geom=None,
            submitted_at=datetime.now(timezone.utc),
            image_url="https://s3.example.com/photo.jpg",
        )
        assert required_fields_present(report_missing) is False

        report_empty = MagicMock(
            location_geom="GEOM",
            submitted_at=datetime.now(timezone.utc),
            image_url="",
        )
        assert required_fields_present(report_empty) is False


class TestRejectionCheckPipeline:
    def _create_clean_report(self):
        return MagicMock(
            id=10,
            user_id="usr-123",
            location_geom="GEOM",
            submitted_at=datetime.now(timezone.utc) - timedelta(minutes=10),
            image_url="https://s3.example.com/photo.jpg",
        )

    def test_missing_required_field(self):
        report = self._create_clean_report()
        report.image_url = ""
        mock_session = MagicMock()

        passed, reason = rejection_check(report, mock_session)
        assert passed is False
        assert reason == "missing_required_field"

    def test_invalid_location_coordinates_none(self, monkeypatch):
        report = self._create_clean_report()
        mock_session = MagicMock()
        monkeypatch.setattr(rejection_checks, "get_report_coordinates", lambda _r: None)

        passed, reason = rejection_check(report, mock_session)
        assert passed is False
        assert reason == "invalid_location"

    def test_invalid_location_zero_zero(self, monkeypatch):
        report = self._create_clean_report()
        mock_session = MagicMock()
        monkeypatch.setattr(rejection_checks, "get_report_coordinates", lambda _r: (0.0, 0.0))

        passed, reason = rejection_check(report, mock_session)
        assert passed is False
        assert reason == "invalid_location"

    def test_outside_boundary(self, monkeypatch):
        report = self._create_clean_report()
        mock_session = MagicMock()
        monkeypatch.setattr(rejection_checks, "get_report_coordinates", lambda _r: (-10.0, 18.0))

        passed, reason = rejection_check(report, mock_session)
        assert passed is False
        assert reason == "outside_boundary"

    def test_invalid_timestamp(self, monkeypatch):
        report = self._create_clean_report()
        mock_session = MagicMock()
        monkeypatch.setattr(rejection_checks, "get_report_coordinates", lambda _r: (-33.9249, 18.4241))
        monkeypatch.setattr(rejection_checks, "valid_timestamp", lambda _ts: False)

        passed, reason = rejection_check(report, mock_session)
        assert passed is False
        assert reason == "invalid_timestamp"

    def test_missing_photo(self, monkeypatch):
        report = self._create_clean_report()
        mock_session = MagicMock()
        monkeypatch.setattr(rejection_checks, "required_fields_present", lambda _r: True)
        monkeypatch.setattr(rejection_checks, "get_report_coordinates", lambda _r: (-33.9249, 18.4241))
        monkeypatch.setattr(rejection_checks, "valid_timestamp", lambda _ts: True)
        report.image_url = None

        passed, reason = rejection_check(report, mock_session)
        assert passed is False
        assert reason == "missing_photo"

    def test_duplicate_submission(self, monkeypatch):
        report = self._create_clean_report()
        mock_session = MagicMock()
        monkeypatch.setattr(rejection_checks, "get_report_coordinates", lambda _r: (-33.9249, 18.4241))
        monkeypatch.setattr(rejection_checks, "valid_timestamp", lambda _ts: True)
        monkeypatch.setattr(rejection_checks, "duplicate_submission", lambda _r, _s: True)

        passed, reason = rejection_check(report, mock_session)
        assert passed is False
        assert reason == "duplicate_submission"

    def test_location_in_water(self, monkeypatch):
        report = self._create_clean_report()
        mock_session = MagicMock()
        monkeypatch.setattr(rejection_checks, "get_report_coordinates", lambda _r: (-33.9249, 18.4241))
        monkeypatch.setattr(rejection_checks, "valid_timestamp", lambda _ts: True)
        monkeypatch.setattr(rejection_checks, "duplicate_submission", lambda _r, _s: False)
        monkeypatch.setattr(rejection_checks, "on_land", lambda _lat, _lng: False)

        passed, reason = rejection_check(report, mock_session)
        assert passed is False
        assert reason == "location_in_water"

    def test_location_check_unavailable_manual_review(self, monkeypatch):
        report = self._create_clean_report()
        mock_session = MagicMock()
        monkeypatch.setattr(rejection_checks, "get_report_coordinates", lambda _r: (-33.9249, 18.4241))
        monkeypatch.setattr(rejection_checks, "valid_timestamp", lambda _ts: True)
        monkeypatch.setattr(rejection_checks, "duplicate_submission", lambda _r, _s: False)

        def raise_unavailable(_lat, _lng):
            raise LocationCheckUnavailable("Mapbox offline")

        monkeypatch.setattr(rejection_checks, "on_land", raise_unavailable)

        passed, reason = rejection_check(report, mock_session)
        assert passed is False
        assert reason == "manual_review"

    def test_rejection_check_all_passed(self, monkeypatch):
        report = self._create_clean_report()
        mock_session = MagicMock()
        monkeypatch.setattr(rejection_checks, "get_report_coordinates", lambda _r: (-33.9249, 18.4241))
        monkeypatch.setattr(rejection_checks, "valid_timestamp", lambda _ts: True)
        monkeypatch.setattr(rejection_checks, "duplicate_submission", lambda _r, _s: False)
        monkeypatch.setattr(rejection_checks, "on_land", lambda _lat, _lng: True)

        passed, reason = rejection_check(report, mock_session)
        assert passed is True
        assert reason is None