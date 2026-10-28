from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock
import pytest

from app.backend.src.services.guests import guests_dashboard
from app.backend.src.services.guests.guests_dashboard import (
    calculate_time_ago,
    get_guest_dashboard_data,
)


class TestCalculateTimeAgo:
    def test_just_now(self, monkeypatch):
        fixed_now = datetime(2026, 6, 1, 12, 0, 30, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(guests_dashboard, "datetime", mock_dt)

        reported_at = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported_at) == "just now"

    def test_minutes_ago(self, monkeypatch):
        fixed_now = datetime(2026, 6, 1, 12, 15, 0, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(guests_dashboard, "datetime", mock_dt)

        reported_at = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported_at) == "15 min ago"

    def test_one_hour_ago(self, monkeypatch):
        fixed_now = datetime(2026, 6, 1, 13, 10, 0, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(guests_dashboard, "datetime", mock_dt)

        reported_at = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported_at) == "1 hr ago"

    def test_multiple_hours_ago(self, monkeypatch):
        fixed_now = datetime(2026, 6, 1, 16, 0, 0, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(guests_dashboard, "datetime", mock_dt)

        reported_at = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported_at) == "4 hrs ago"

    def test_one_day_ago(self, monkeypatch):
        fixed_now = datetime(2026, 6, 2, 13, 0, 0, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(guests_dashboard, "datetime", mock_dt)

        reported_at = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported_at) == "1 day ago"

    def test_multiple_days_ago(self, monkeypatch):
        fixed_now = datetime(2026, 6, 5, 12, 0, 0, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(guests_dashboard, "datetime", mock_dt)

        reported_at = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported_at) == "4 days ago"


class TestGetGuestDashboardData:
    def test_get_guest_dashboard_data_success_with_reports_and_env(self, monkeypatch):
        mock_db = MagicMock()

        mock_fire = MagicMock()
        mock_fire.id = "fire-001"
        mock_fire.reference_number = "FR-2026-001"
        mock_fire.location_text = "Table Mountain Slopes"
        mock_fire.status = MagicMock(value="verified")
        mock_fire.boundary_radius = 2.5
        mock_fire.location_geom = "MOCK_GEOM"
        mock_fire.submitted_at = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)

        mock_dist_m = 3500.0

        query_mock = MagicMock()
        query_mock.filter.return_value.order_by.return_value.all.return_value = [
            (mock_fire, mock_dist_m)
        ]
        mock_db.query.return_value = query_mock

        mock_shape = MagicMock()
        mock_shape.x = 18.4241
        mock_shape.y = -33.9249
        monkeypatch.setattr(guests_dashboard, "to_shape", lambda _geom: mock_shape)

        mock_env = {
            "temperature": 26.5,
            "humidity": 45.0,
            "wind_speed": 18.0,
        }
        monkeypatch.setattr(
            guests_dashboard,
            "get_current_environment_vars",
            lambda lat, lng: mock_env,
        )

        result = get_guest_dashboard_data(
            db=mock_db, lat=-33.9249, lng=18.4241, radius_km=20
        )

        assert result["environment_variables"] == mock_env
        assert len(result["nearby_reports"]) == 1

        report = result["nearby_reports"][0]
        assert report["id"] == "fire-001"
        assert report["reference_number"] == "FR-2026-001"
        assert report["location_text"] == "Table Mountain Slopes"
        assert report["lat"] == -33.9249
        assert report["lng"] == 18.4241
        assert report["status"] == "verified"
        assert report["boundary_radius"] == 2.5
        assert report["distance"] == 3.5
        assert isinstance(report["time_ago"], str)

    def test_get_guest_dashboard_data_handles_env_exception(self, monkeypatch):
        mock_db = MagicMock()
        query_mock = MagicMock()
        query_mock.filter.return_value.order_by.return_value.all.return_value = []
        mock_db.query.return_value = query_mock

        def raise_env_error(lat, lng):
            raise RuntimeError("Weather provider timeout")

        monkeypatch.setattr(
            guests_dashboard,
            "get_current_environment_vars",
            raise_env_error,
        )

        result = get_guest_dashboard_data(db=mock_db, lat=-33.9249, lng=18.4241)

        assert result["nearby_reports"] == []
        assert result["environment_variables"] is None