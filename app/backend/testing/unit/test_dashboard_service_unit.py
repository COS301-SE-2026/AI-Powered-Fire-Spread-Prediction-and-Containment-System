from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock
import pytest

from app.backend.src.services.admin import dashboard_service
from app.backend.src.services.admin.dashboard_service import (
    as_aware,
    calculate_time_ago,
    get_top_metrics,
    user_display_name,
    get_recent_activity,
    get_weekly_incident_counts,
    get_system_metrics,
    dashboard_summary,
)


class TestAsAware:
    def test_as_aware_none(self):
        assert as_aware(None) is None

    def test_as_aware_naive(self):
        dt_naive = datetime(2026, 6, 1, 12, 0, 0)
        aware = as_aware(dt_naive)
        assert aware.tzinfo == timezone.utc
        assert aware.year == 2026

    def test_as_aware_already_aware(self):
        tz_custom = timezone(timedelta(hours=2))
        dt_aware = datetime(2026, 6, 1, 12, 0, 0, tzinfo=tz_custom)
        res = as_aware(dt_aware)
        assert res.tzinfo == tz_custom


class TestCalculateTimeAgo:
    def test_just_now(self, monkeypatch):
        fixed_now = datetime(2026, 6, 1, 12, 0, 30, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(dashboard_service, "datetime", mock_dt)

        reported = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported) == "just now"

    def test_minutes_ago(self, monkeypatch):
        fixed_now = datetime(2026, 6, 1, 12, 15, 0, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(dashboard_service, "datetime", mock_dt)

        reported = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported) == "15 min ago"

    def test_one_hour_ago(self, monkeypatch):
        fixed_now = datetime(2026, 6, 1, 13, 5, 0, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(dashboard_service, "datetime", mock_dt)

        reported = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported) == "1 hr ago"

    def test_multiple_hours_ago(self, monkeypatch):
        fixed_now = datetime(2026, 6, 1, 17, 0, 0, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(dashboard_service, "datetime", mock_dt)

        reported = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported) == "5 hrs ago"

    def test_one_day_ago(self, monkeypatch):
        fixed_now = datetime(2026, 6, 2, 13, 0, 0, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(dashboard_service, "datetime", mock_dt)

        reported = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported) == "1 day ago"

    def test_multiple_days_ago(self, monkeypatch):
        fixed_now = datetime(2026, 6, 5, 12, 0, 0, tzinfo=timezone.utc)
        mock_dt = MagicMock(wraps=datetime)
        mock_dt.now.return_value = fixed_now
        monkeypatch.setattr(dashboard_service, "datetime", mock_dt)

        reported = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert calculate_time_ago(reported) == "4 days ago"


class TestUserDisplayName:
    def test_user_is_none(self):
        assert user_display_name(None) == "Unknown user"

    def test_full_first_and_last_name(self):
        user = MagicMock(spec=["first_name", "last_name", "name", "email"])
        user.first_name = "Jane"
        user.last_name = "Doe"
        user.email = "jane@example.com"
        assert user_display_name(user) == "Jane Doe"

    def test_only_first_name(self):
        user = MagicMock(spec=["first_name", "last_name", "name", "email"])
        user.first_name = "Jane"
        user.last_name = None
        user.email = "jane@example.com"
        assert user_display_name(user) == "Jane"

    def test_fallback_to_name_attribute(self):
        user = MagicMock(spec=["first_name", "last_name", "name", "email"])
        user.first_name = None
        user.last_name = None
        user.name = "Officer Doe"
        user.email = "officer@example.com"
        assert user_display_name(user) == "Officer Doe"

    def test_fallback_to_email(self):
        user = MagicMock(spec=["first_name", "last_name", "name", "email"])
        user.first_name = None
        user.last_name = None
        user.name = None
        user.email = "plain@example.com"
        assert user_display_name(user) == "plain@example.com"


class TestGetTopMetrics:
    def test_get_top_metrics_status_okay(self):
        db = MagicMock()
        q1 = MagicMock()
        q1.filter.return_value.scalar.return_value = 5  # active_fires <= 10

        q2 = MagicMock()
        q2.filter.return_value.scalar.return_value = 2  # pending_approvals

        q3 = MagicMock()
        q3.scalar.return_value = 40  # total_users

        db.query.side_effect = [q1, q2, q3]

        metrics = get_top_metrics(db)
        assert metrics == {
            "active_fires": 5,
            "pending_approvals": 2,
            "total_users": 40,
            "system_status": "OKAY",
        }

    def test_get_top_metrics_status_alert(self):
        db = MagicMock()
        q1 = MagicMock()
        q1.filter.return_value.scalar.return_value = 15  # active_fires > 10

        q2 = MagicMock()
        q2.filter.return_value.scalar.return_value = 0

        q3 = MagicMock()
        q3.scalar.return_value = 100

        db.query.side_effect = [q1, q2, q3]

        metrics = get_top_metrics(db)
        assert metrics["system_status"] == "ALERT"


class TestGetRecentActivity:
    def test_get_recent_activity_combined_and_sorted(self):
        db = MagicMock()

        t1 = datetime(2026, 6, 1, 10, 0, 0, tzinfo=timezone.utc)
        t2 = datetime(2026, 6, 1, 11, 0, 0, tzinfo=timezone.utc)
        t3 = datetime(2026, 6, 1, 8, 0, 0, tzinfo=timezone.utc)

        mock_fire_1 = MagicMock(id=101, location_text="Cape Town North", submitted_at=t1)
        mock_fire_2 = MagicMock(id=102, location_text="Old Sector", submitted_at=t3)

        q_fires = MagicMock()
        q_fires.order_by.return_value.limit.return_value.all.return_value = [mock_fire_1, mock_fire_2]

        mock_user = MagicMock(spec=["first_name", "last_name", "name", "email"])
        mock_user.first_name = "Alice"
        mock_user.last_name = "Smith"
        mock_user.email = "alice@example.com"

        mock_rr = MagicMock(
            request_id="req-99",
            reviewed_at=t2,
            status=MagicMock(value="approved"),
            requested_role=MagicMock(value="firefighter"),
        )

        q_rr = MagicMock()
        q_rr.outerjoin.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            (mock_rr, mock_user)
        ]

        db.query.side_effect = [q_fires, q_rr]

        activity = get_recent_activity(db, limit=2)

        assert len(activity) == 2
        assert activity[0]["id"] == "role-req-99"
        assert activity[0]["message"] == "Role approved - Alice Smith (firefighter)"
        assert "_sort_ts" not in activity[0]

        assert activity[1]["id"] == "fire-101"
        assert activity[1]["message"] == "New fire reported - Cape Town North"
        assert "_sort_ts" not in activity[1]


class TestGetWeeklyIncidentCounts:
    def test_get_weekly_incident_counts_distribution(self):
        db = MagicMock()

        mon_report_1 = MagicMock(submitted_at=datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc))
        mon_report_2 = MagicMock(submitted_at=datetime(2026, 6, 1, 15, 0, tzinfo=timezone.utc))
        tue_report = MagicMock(submitted_at=datetime(2026, 6, 2, 8, 0, tzinfo=timezone.utc))
        other_report = MagicMock(submitted_at=MagicMock(strftime=MagicMock(return_value="UnkDay")))

        q = MagicMock()
        q.filter.return_value.all.return_value = [mon_report_1, mon_report_2, tue_report, other_report]
        db.query.return_value = q

        counts = get_weekly_incident_counts(db, days=7)
        counts_dict = {item["day"]: item["count"] for item in counts}

        assert counts_dict["Mon"] == 2
        assert counts_dict["Tue"] == 1
        assert counts_dict["Wed"] == 0
        assert counts_dict["Thu"] == 0
        assert counts_dict["Fri"] == 0
        assert counts_dict["Sat"] == 0
        assert counts_dict["Sun"] == 0


class TestGetSystemMetricsAndSummary:
    def test_get_system_metrics(self):
        db = MagicMock()
        res = get_system_metrics(db)
        assert res == {
            "predictions_completed": 0,
            "model_health": "Unknown",
            "avg_confidence_percent": 0,
            "last_sync_time": "Not yet tracked",
        }

    def test_dashboard_summary(self, monkeypatch):
        db = MagicMock()

        monkeypatch.setattr(dashboard_service, "get_top_metrics", lambda _db: {"active_fires": 1})
        monkeypatch.setattr(dashboard_service, "get_recent_activity", lambda _db: [{"id": "act-1"}])
        monkeypatch.setattr(dashboard_service, "get_weekly_incident_counts", lambda _db: [{"day": "Mon", "count": 1}])
        monkeypatch.setattr(dashboard_service, "get_system_metrics", lambda _db: {"model_health": "Good"})

        summary = dashboard_summary(db)

        assert summary["top_metrics"] == {"active_fires": 1}
        assert summary["activity_log"] == [{"id": "act-1"}]
        assert summary["weekly_incidents"] == [{"day": "Mon", "count": 1}]
        assert summary["system_metrics"] == {"model_health": "Good"}