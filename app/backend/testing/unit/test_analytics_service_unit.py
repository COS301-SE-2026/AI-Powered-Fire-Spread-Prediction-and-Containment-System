from datetime import datetime, timezone
from unittest.mock import MagicMock
import pytest

from app.backend.src.enums.role_request_status import RequestStatus
from app.backend.src.enums.user_role import UserRole
from app.backend.src.models.role_request import RoleRequest
from app.backend.src.models.users import User
from app.backend.src.schemas.admin_analytics import AnalyticsOverviewResponse, KPIs
from app.backend.src.schemas.role_request import RoleRequestResponse, UserSummary
from app.backend.src.services.admin import analytics_service
from app.backend.src.services.admin.analytics_service import (
    analytics_overview,
    get_kpis,
    get_pending_role_reqs,
)


class TestGetKpis:
    def test_get_kpis_no_active_users_raises_value_error(self):
        db = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.count.return_value = 0
        db.query.return_value = mock_query

        with pytest.raises(ValueError, match="Unable to get user metrics"):
            get_kpis(db)

    def test_get_kpis_success(self):
        db = MagicMock()

        q_users = MagicMock()
        q_users.filter.return_value.count.return_value = 25

        q_pending = MagicMock()
        q_pending.filter.return_value.count.return_value = 4

        q_firefighters = MagicMock()
        q_firefighters.filter.return_value.count.return_value = 7

        q_admins = MagicMock()
        q_admins.filter.return_value.count.return_value = 2

        db.query.side_effect = [q_users, q_pending, q_firefighters, q_admins]

        kpis = get_kpis(db)

        assert isinstance(kpis, KPIs)
        assert kpis.total_users == 25
        assert kpis.pending_role_requests == 4
        assert kpis.total_firefighters == 7
        assert kpis.total_admins == 2
        assert db.query.call_count == 4


class TestGetPendingRoleReqs:
    def test_invalid_limit_raises_value_error(self):
        db = MagicMock()

        with pytest.raises(ValueError, match="limit has to be a positive value"):
            get_pending_role_reqs(db, limit=0)

        with pytest.raises(ValueError, match="limit has to be a positive value"):
            get_pending_role_reqs(db, limit=-5)

    def test_get_pending_role_reqs_empty(self):
        db = MagicMock()
        q_rr = MagicMock()
        q_rr.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        db.query.return_value = q_rr

        results = get_pending_role_reqs(db, limit=10)
        assert results == []

    def test_get_pending_role_reqs_with_matching_and_missing_users(self):
        db = MagicMock()

        now = datetime.now(timezone.utc)

        req1 = MagicMock(
            request_id="req-1",
            user_id="usr-1",
            requested_role=UserRole.firefighter,
            current_role=UserRole.user,
            status=RequestStatus.pending,
            created_at=now,
            reviewed_at=None,
            reviewed_by=None,
        )
        req2 = MagicMock(
            request_id="req-2",
            user_id="usr-nonexistent",
            requested_role=UserRole.admin,
            current_role=UserRole.firefighter,
            status=RequestStatus.pending,
            created_at=now,
            reviewed_at=None,
            reviewed_by=None,
        )

        q_rr = MagicMock()
        q_rr.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            req1,
            req2,
        ]

        mock_user = MagicMock()
        mock_user.id = "usr-1"
        mock_user.name = "John"
        mock_user.surname = "Doe"
        mock_user.email = "john.doe@example.com"
        mock_user.license_number = None
        mock_user.firefighter_license_id = None

        q_user1 = MagicMock()
        q_user1.filter.return_value.first.return_value = mock_user

        q_user2 = MagicMock()
        q_user2.filter.return_value.first.return_value = None

        db.query.side_effect = [q_rr, q_user1, q_user2]

        results = get_pending_role_reqs(db)

        assert len(results) == 1
        assert isinstance(results[0], RoleRequestResponse)
        assert results[0].request_id == "req-1"
        assert results[0].user.id == "usr-1"
        assert results[0].user.name == "John"
        assert results[0].user.surname == "Doe"
        assert results[0].user.email == "john.doe@example.com"
        assert results[0].requested_role == UserRole.firefighter
        assert results[0].current_role == UserRole.user
        assert results[0].status == RequestStatus.pending


class TestAnalyticsOverview:
    def test_analytics_overview_builds_response(self, monkeypatch):
        db = MagicMock()

        mock_kpis = KPIs(
            total_users=10,
            pending_role_requests=3,
            total_firefighters=2,
            total_admins=1,
        )

        dummy_user = UserSummary.model_construct(
            id="usr-1",
            name="Alice",
            surname="Smith",
            email="alice@example.com",
            license_number=None,
        )

        mock_req = RoleRequestResponse.model_construct(
            request_id="req-1",
            user=dummy_user,
            requested_role=UserRole.firefighter,
            current_role=UserRole.user,
            status=RequestStatus.pending,
            created_at=datetime.now(timezone.utc),
            reviewed_at=None,
            reviewed_by=None,
        )

        monkeypatch.setattr(analytics_service, "get_kpis", lambda _db: mock_kpis)
        monkeypatch.setattr(
            analytics_service, "get_pending_role_reqs", lambda _db: [mock_req]
        )

        response = analytics_overview(db)

        assert isinstance(response, AnalyticsOverviewResponse)
        assert response.kpis == mock_kpis
        assert response.pending_requests == [mock_req]