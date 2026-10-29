from datetime import datetime, timezone
from unittest.mock import MagicMock
import pytest

try:
    import app.backend.src.services.users.role_request as role_request_module
except ImportError:
    import app.backend.src.services.admin.role_request as role_request_module

from app.backend.src.enums.role_request_status import RequestStatus
from app.backend.src.enums.user_role import UserRole
from app.backend.src.models.role_request import RoleRequest
from app.backend.src.schemas.role_request import RoleRequestList


class TestGetRoleRequests:
    def test_get_role_requests_delegates(self, monkeypatch):
        get_role_requests_fn = getattr(role_request_module, "get_role_requests", None)
        if get_role_requests_fn is None:
            pytest.skip("get_role_requests is not implemented in this module")

        mock_db = MagicMock()
        mock_requests = [MagicMock(), MagicMock()]
        mock_db.query.return_value.all.return_value = mock_requests

        mock_list = MagicMock(return_value="mock_result_list")
        monkeypatch.setattr(role_request_module, "role_request_list", mock_list)

        result = get_role_requests_fn(mock_db)

        mock_db.query.assert_called_once_with(RoleRequest)
        mock_list.assert_called_once_with(mock_db, mock_requests)
        assert result == "mock_result_list"


class TestApproveRoleRequest:
    def test_approve_request_not_found_returns_none(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = role_request_module.approve_role_request("req_missing", "admin_1", mock_db)
        assert result is None
        mock_db.commit.assert_not_called()

    def test_approve_non_pending_request_raises_value_error(self):
        mock_db = MagicMock()
        mock_req = MagicMock(status=RequestStatus.approved)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_req

        with pytest.raises(ValueError, match="Role is already approved"):
            role_request_module.approve_role_request("req_01", "admin_1", mock_db)

    def test_approve_user_not_found_raises_value_error(self):
        mock_db = MagicMock()
        mock_req = MagicMock(status=RequestStatus.pending, user_id="usr_missing")
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_req, None]

        with pytest.raises(ValueError, match="User not found!!"):
            role_request_module.approve_role_request("req_01", "admin_1", mock_db)

    def test_approve_success(self):
        mock_db = MagicMock()
        mock_req = MagicMock(
            status=RequestStatus.pending,
            user_id="usr_01",
            requested_role=UserRole.firefighter,
        )
        mock_user = MagicMock(id="usr_01", role=UserRole.user)
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_req, mock_user]

        result = role_request_module.approve_role_request("req_01", "admin_1", mock_db)

        assert mock_user.role == UserRole.firefighter
        assert mock_req.status == RequestStatus.approved
        assert mock_req.reviewed_by == "admin_1"
        assert isinstance(mock_req.reviewed_at, datetime)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_req)
        assert result is mock_req


class TestRejectRoleRequest:
    def test_reject_request_not_found_returns_none(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = role_request_module.reject_role_request("req_missing", "admin_1", mock_db)
        assert result is None
        mock_db.commit.assert_not_called()

    def test_reject_non_pending_request_raises_value_error(self):
        mock_db = MagicMock()
        mock_req = MagicMock(status=RequestStatus.rejected)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_req

        with pytest.raises(ValueError, match="Role is already rejected"):
            role_request_module.reject_role_request("req_01", "admin_1", mock_db)

    def test_reject_user_not_found_raises_value_error(self):
        mock_db = MagicMock()
        mock_req = MagicMock(status=RequestStatus.pending, user_id="usr_missing")
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_req, None]

        with pytest.raises(ValueError, match="User not found!!"):
            role_request_module.reject_role_request("req_01", "admin_1", mock_db)

    def test_reject_success(self):
        mock_db = MagicMock()
        mock_req = MagicMock(status=RequestStatus.pending, user_id="usr_01")
        mock_user = MagicMock(id="usr_01")
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_req, mock_user]

        result = role_request_module.reject_role_request("req_01", "admin_1", mock_db)

        assert mock_req.status == RequestStatus.rejected
        assert mock_req.reviewed_by == "admin_1"
        assert isinstance(mock_req.reviewed_at, datetime)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_req)
        assert result is mock_req


class TestRevokeRoleRequest:
    def test_revoke_request_not_found_returns_none(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = role_request_module.revoke_role_request("req_missing", "admin_1", mock_db)
        assert result is None
        mock_db.commit.assert_not_called()

    def test_revoke_non_approved_request_raises_value_error(self):
        mock_db = MagicMock()
        mock_req = MagicMock(status=RequestStatus.pending)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_req

        with pytest.raises(ValueError, match="Only approved reqeusts may be revoked!!"):
            role_request_module.revoke_role_request("req_01", "admin_1", mock_db)

    def test_revoke_user_not_found_raises_value_error(self):
        mock_db = MagicMock()
        mock_req = MagicMock(status=RequestStatus.approved, user_id="usr_missing")
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_req, None]

        with pytest.raises(ValueError, match="User not found!!"):
            role_request_module.revoke_role_request("req_01", "admin_1", mock_db)

    def test_revoke_success(self):
        mock_db = MagicMock()
        mock_req = MagicMock(
            status=RequestStatus.approved,
            user_id="usr_01",
            current_role=UserRole.user,
        )
        mock_user = MagicMock(id="usr_01", role=UserRole.firefighter)
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_req, mock_user]

        result = role_request_module.revoke_role_request("req_01", "admin_1", mock_db)

        assert mock_user.role == UserRole.user
        assert mock_req.status == RequestStatus.revoked
        assert mock_req.reviewed_by == "admin_1"
        assert isinstance(mock_req.reviewed_at, datetime)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_req)
        assert result is mock_req


class TestSearchReportTableAndList:
    def test_search_report_table(self, monkeypatch):
        mock_db = MagicMock()
        mock_records = [MagicMock()]
        mock_db.query.return_value.outerjoin.return_value.filter.return_value.all.return_value = mock_records

        mock_role_request_list = MagicMock(return_value="mock_search_result")
        monkeypatch.setattr(role_request_module, "role_request_list", mock_role_request_list)

        result = role_request_module.search_report_table(mock_db, key=" Alice ")

        mock_role_request_list.assert_called_once_with(mock_db, mock_records)
        assert result == "mock_search_result"

    def test_role_request_list_populates_trust_metrics(self, monkeypatch):
        mock_db = MagicMock()

        req1 = MagicMock(spec=RoleRequest)
        req1.user_id = "usr_01"
        req2 = MagicMock(spec=RoleRequest)
        req2.user_id = "usr_02"

        monkeypatch.setattr(
            role_request_module,
            "reporter_report_counts",
            lambda ids, db: {"usr_01": (5, 1), "usr_02": (0, 0)},
        )
        monkeypatch.setattr(
            role_request_module,
            "trust_score_from_counts",
            lambda v, r: 83.3 if v == 5 else None,
        )

        fake_item1 = MagicMock()
        fake_item2 = MagicMock()

        mock_validate = MagicMock(side_effect=[fake_item1, fake_item2])
        monkeypatch.setattr(role_request_module.RoleRequestResponse, "model_validate", mock_validate)

        res = role_request_module.role_request_list(mock_db, [req1, req2])

        assert isinstance(res, RoleRequestList)
        assert res.total == 2
        assert len(res.data) == 2

        assert fake_item1.reports_verified == 5
        assert fake_item1.reports_rejected == 1
        assert fake_item1.trust_score == 83.3

        assert fake_item2.reports_verified == 0
        assert fake_item2.reports_rejected == 0
        assert fake_item2.trust_score is None