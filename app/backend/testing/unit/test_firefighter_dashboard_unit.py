from datetime import datetime, timezone
from unittest.mock import MagicMock
import pytest

from app.backend.src.services.firefighter import firefighter_dashboard
from app.backend.src.services.firefighter.firefighter_dashboard import (
    calculate_time_ago,
    get_nearby_fires,
    get_current_environment_vars,
)


class TestCalculateTimeAgo:
    def test_just_now(self, monkeypatch):
        fixed_now = datetime(2026, 6, 1, 12, 0, 30, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(firefighter_dashboard, "datetime", mock_dt)

        reported_at = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported_at) == "just now"

    def test_minutes_ago(self, monkeypatch):
        fixed_now = datetime(2026, 6, 1, 12, 15, 0, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(firefighter_dashboard, "datetime", mock_dt)

        reported_at = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported_at) == "15 min ago"

    def test_one_hour_ago(self, monkeypatch):
        fixed_now = datetime(2026, 6, 1, 13, 10, 0, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(firefighter_dashboard, "datetime", mock_dt)

        reported_at = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported_at) == "1 hr ago"

    def test_multiple_hours_ago(self, monkeypatch):
        fixed_now = datetime(2026, 6, 1, 16, 0, 0, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(firefighter_dashboard, "datetime", mock_dt)

        reported_at = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported_at) == "4 hrs ago"

    def test_one_day_ago(self, monkeypatch):
        fixed_now = datetime(2026, 6, 2, 13, 0, 0, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(firefighter_dashboard, "datetime", mock_dt)

        reported_at = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported_at) == "1 day ago"

    def test_multiple_days_ago(self, monkeypatch):
        fixed_now = datetime(2026, 6, 5, 12, 0, 0, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(firefighter_dashboard, "datetime", mock_dt)

        reported_at = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported_at) == "4 days ago"


class TestGetNearbyFires:
    def test_get_nearby_fires_success(self, monkeypatch):
        mock_db = MagicMock()

        mock_fire = MagicMock()
        mock_fire.location_text = "Table Mountain Fire"
        mock_fire.location_geom = "MOCK_GEOM"
        mock_fire.submitted_at = datetime(2026, 6, 1, 11, 0, 0, tzinfo=timezone.utc)
        mock_fire.status = "verified"

        mock_shape = MagicMock()
        mock_shape.x = 18.4241
        mock_shape.y = -33.9249
        monkeypatch.setattr(firefighter_dashboard, "to_shape", lambda _geom: mock_shape)

        dist_m = 4500.0
        query_mock = MagicMock()
        query_mock.filter.return_value.add_columns.return_value.order_by.return_value.all.return_value = [
            (mock_fire, dist_m)
        ]
        mock_db.query.return_value = query_mock

        result = get_nearby_fires(db=mock_db, lat=-33.9249, lng=18.4241, radius_km=20)

        assert result["total"] == 1
        item = result["data"][0]
        assert item["location_text"] == "Table Mountain Fire"
        assert item["distance"] == 4.5
        assert isinstance(item["time_ago"], str)
        assert item["status"] == "verified"
        assert item["latitude"] == -33.9249
        assert item["longitude"] == 18.4241

    def test_get_nearby_fires_empty(self):
        mock_db = MagicMock()
        query_mock = MagicMock()
        query_mock.filter.return_value.add_columns.return_value.order_by.return_value.all.return_value = []
        mock_db.query.return_value = query_mock

        result = get_nearby_fires(db=mock_db, lat=-33.9249, lng=18.4241, radius_km=10)

        assert result == {"data": [], "total": 0}


class TestGetCurrentEnvironmentVars:
    def test_get_current_environment_vars(self, monkeypatch):
        mock_conditions = {
            "temperature": 27.5,
            "humidity": 30.0,
            "wind_speed": 15.0,
            "wind_direction": 180.0,
            "fdi_band": "VERY DANGEROUS",
            "fdi": 82.5,
            "fdi_color": "orange",
        }
        monkeypatch.setattr(
            firefighter_dashboard,
            "get_fuel_conditions",
            lambda lat, lng: mock_conditions,
        )

        env = get_current_environment_vars(lat=-33.9249, lng=18.4241)

        assert env == {
            "temperature": 27.5,
            "humidity": 30.0,
            "wind": 15.0,
            "wind_dir": 180.0,
            "fire_danger": "VERY DANGEROUS",
            "fdi": 82.5,
            "fdi_color": "orange",
        }