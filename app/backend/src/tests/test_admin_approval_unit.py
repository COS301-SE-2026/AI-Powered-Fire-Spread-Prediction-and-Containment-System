
from datetime import datetime

import pytest
from unittest.mock import MagicMock

from enum import Enum

# Stubs for unit tests
import sys

class RoleRequest:
    """ORM Stand-in"""
    request_id = "request_id"
    def __init__(self, **kwargs):
        for i, j in kwargs.items():
            setattr(self, i, j)

class User:
    id = "id"
    def __init__(self, **kwargs):
        for i, j in kwargs.items():
            setattr(self, i, j)

class RequestStatus(Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    revoked = "revoked"

role_request_module = MagicMock()
role_request_module.RoleRequest = RoleRequest

users_module = MagicMock()
users_module.User = User

enums_module = MagicMock()
enums_module.RequestStatus = RequestStatus

sys.modules.setdefault("models", MagicMock())
sys.modules.setdefault("models.role_request", role_request_module)
sys.modules.setdefault("models.users", users_module)
sys.modules.setdefault("enums", MagicMock())
sys.modules.setdefault("enums.role_request_status", enums_module)

from services.admin.role_request import(
    get_role_requests,
    approve_role_request,
    reject_role_request,
    revoke_role_request,
)

def make_db():
    """New Mock Session"""
    return MagicMock()

def make_request(**kwargs) -> RoleRequest:
    defaults = dict(
        request_id = "req-1",
        user_id = "user-1",
        full_name = "John Doe",
        email = "john@doe.com",
        requested_role = "firefighter",
        current_role="guest",
        status = RequestStatus.pending,
        reviewed_by=None,
        reviewed_at=None,
        created_at = datetime(2026, 5, 27),
    )
    defaults.update(kwargs)
    return RoleRequest(**defaults)

def make_user(**kwargs) -> User:
    defaults = dict(
        id = "user-1",
        role = "guest",
    )
    defaults.update(kwargs)
    return User(**defaults)

def query_side_effect(db, model_map: dict):
    """Make db.query(ModelClass) return mock where .filter().first() finds value in model_map. Keyed by model class"""
    def query(model):
        matched_data = None
        for stub, data in model_map.items():
            if model is stub:
                matched_data = data
                break

        chain_query = MagicMock()
        chain_query.all.return_value = (
            matched_data if isinstance(matched_data, list) else ([] if matched_data is None else [matched_data])
        )

        filter_mock = MagicMock()
        filter_mock.first.return_value = matched_data
        chain_query.filter.return_value = filter_mock
        return chain_query

    db.query.side_effect = query
    return db


# Test get_role_requests
class TestGetRoleRequests:
    def test_returns_all_requests(self):
        db = make_db()
        reqs = [make_request(request_id = f"req-{i}") for i in range(3)]
        db.query.return_value.all.return_value = reqs

        result = get_role_requests(db=db)

        assert result["total"] == 3
        assert len(result["data"]) == 3

    def test_empty_db(self):
        db = make_db()
        db.query.return_value.all.return_value = []

        result = get_role_requests(db=db)

        assert result["total"] == 0
        assert result["data"] == []


# Test approve_role_request
class TestApproveRoleRequest:
    def test_approve_pending_approves(self):
        req = make_request(role = "firefighter", status = RequestStatus.pending)
        user = make_user()
        db = query_side_effect(make_db(), {RoleRequest: req, User: user})

        result = approve_role_request("req-1", "user-1", db=db)

        assert result.status == RequestStatus.approved
        assert user.role == "firefighter"
        db.commit.assert_called_once()

    def test_approve_non_firefighter(self):
        req = make_request(role="admin", status=RequestStatus.pending)
        user = make_user()
        db = query_side_effect(make_db(), {RoleRequest: req, User: user})

        result = approve_role_request("req-1", "admin-1", db=db)

        assert result.status == RequestStatus.approved
        assert user.role == "admin"

    def test_approve_nonexistent_request(self):
        db = query_side_effect(make_db(), {RoleRequest: None})

        result = approve_role_request("no-such-id", "admin-1", db=db)

        assert result is None

    def test_approved_already_approved(self):
        req = make_request(status=RequestStatus.approved)
        db = query_side_effect(make_db(), {RoleRequest: req})

        with pytest.raises(ValueError):
            approve_role_request("req-1", "admin-1", db=db)

    def test_approved_already_rejected(self):
        req = make_request(status=RequestStatus.rejected)
        db = query_side_effect(make_db(), {RoleRequest: req})

        with pytest.raises(ValueError):
            approve_role_request("req-1","admin-1", db=db)

    def test_approve_with_no_matching_user(self):
        """User lookup returns none. Raise 404 instead of silent succeed"""
        req = make_request(role = "admin", status=RequestStatus.pending)
        db = query_side_effect(make_db(), {RoleRequest: req, User: None})

        with pytest.raises(ValueError):
            approve_role_request("req-1","admin-1", db=db)


# Test reject_role_request
class TestRejectRoleRequest:
    def test_reject_pending_request(self):
        req = make_request(status=RequestStatus.pending)
        user = make_user()
        db = query_side_effect(make_db(), {RoleRequest: req, User: user})

        result = reject_role_request("req-1", "admin-1", db=db)

        assert result.status == RequestStatus.rejected
        db.commit.assert_called_once()

    def test_reject_nonexistent(self):
        db = query_side_effect(make_db(), {RoleRequest: None})

        result = reject_role_request("no-such-id", "admin-1", db=db)

        assert result is None

    def test_reject_already_processed(self):
        for already_done in (RequestStatus.approved, RequestStatus.rejected, RequestStatus.revoked):
            req = make_request(status = already_done)
            db = query_side_effect(make_db(), {RoleRequest: req})

            with pytest.raises(ValueError):
                reject_role_request("req-1", "admin-1", db=db)

# Test revoke_role_request
class TestRevokeRoleRequest:
    def test_revoke_approved(self):     # demotes user to guest
        req = make_request(status = RequestStatus.approved, current_role = "guest")
        user = make_user(role = "firefighter")
        db = query_side_effect(make_db(), {RoleRequest: req, User: user})

        result = revoke_role_request("req-1", "admin-1", db=db)

        assert result.status == RequestStatus.revoked
        assert user.role == "guest"
        db.commit.assert_called_once()

    def test_revoke_nonexistent(self):
        db = query_side_effect(make_db(), {RoleRequest: None})

        result = revoke_role_request("no-such-id", "admin-1", db=db)

        assert result is None

    def test_revoke_pending_request(self):
        req = make_request(status = RequestStatus.pending)
        db = query_side_effect(make_db(), {RoleRequest: req})

        with pytest.raises(ValueError):
            revoke_role_request("req-1", "admin-1", db=db)

    def test_revoke_rejected(self):
        req = make_request(status = RequestStatus.rejected)
        db = query_side_effect(make_db(), {RoleRequest: req})

        with pytest.raises(ValueError):
            revoke_role_request("req-1", "admin-1", db=db)

    def test_revoke_with_no_matching_user(self):
        """User lookup returns None. Raise 404 instead of silent succeed"""
        req = make_request(status=RequestStatus.approved)
        db = query_side_effect(make_db(), {RoleRequest: req, User: None})

        with pytest.raises(ValueError):
            revoke_role_request("req-1", "admin-1", db=db)