import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from datetime import datetime

# Stubs for unit tests

import sys

db_module = MagicMock()
db_module.get_db = MagicMock()

models_module = MagicMock()

class roleRequestDB:
    """ORM Stand-in"""
    def __init__(self, **kwargs):
        for i, j in kwargs.items():
            setattr(self, i, j)

class user:
    def __init__(self, **kwargs):
        for i, j in kwargs.items():
            setattr(self, i, j)

models_module.RoleRequestDB = roleRequestDB
models_module.User = user

sys.modules.setdefault("db", db_module)
sys.modules.setdefault("models", models_module)

from adminRoleApproval import(
    get_role_requests,
    approve_role_request,
    reject_role_request,
    revoke_role_request,
    FIREFIGHTER_LICENSE_IDS,
)

def make_db():
    """New Mock Session"""
    return MagicMock()

def make_request(**kwargs) -> roleRequestDB:
    defaults = dict(
        request_id = "req-1",
        user_id = "user-1",
        full_name = "John Doe",
        email = "john@doe.com",
        role = "firefighter",
        status = "pending",
        firefighter_license_id ="FF-1001",
        created_at = datetime(2026, 5, 27),
    )
    defaults.update(kwargs)
    return roleRequestDB(**defaults)

def make_user(**kwargs) -> user:
    defaults = dict(
        id = "user-1",
        role = "guest",
    )
    defaults.update(kwargs)
    return user(**defaults)

def query_side_effect(db, model_map: dict):
    """Make db.query(ModelClass) return mock where .filter().first() finds value in model_map. Keyed by model class"""
    def query(model):
        results = model_map.get(model)
        q = MagicMock()
        q.filter.return_value.first.return_value = result
        q.all.return_value = result if isinstance(result, list) else ([] if result is None else [result])
        return q
    db.query.side_effects = query
    return db


# Test get_role_requests
class TestGetRoleRequests:
    def test_returns_all_requests(self):
        db = make_db()
        reqs = [make_request(request_id = f"req-{i}") for i in range(3)]
        db.query.return_value.all.return_value = reqs

        result = get_role_requests(db = db)

        assert result["total"] == 3
        assert len(result["data"]) == 3

    def test_empty_db(self):
        db = make_db()
        db.query.return_value.all.return_value = []

        result = get_role_requests(db = db)

        assert result["total"] == 0
        assert result[data] == []

    
# Test approve_role_request
class TestApproveRoleRequest:
    def test_approve_firefighter_with_valid_license(self):
        req = make_request(role = "firefighter", status = "pending", firefighter_license_id = "FF-1001")
        user = make_user(id = "user-1", role = "guest")
        db = query_side_effect(make_db(), {roleRequestDB: req, user: user})

        result = approve_role_request("req-1", db = db)

        assert result.status == "approved"
        assert user.role == "firefighter"
        db.commit.assert_called_once()

    def test_reject_firefighter_with_invalid_license(self):
        req = make_request(role = "firefighter", status = "pending", firefighter_license_id = "FF-INVALID")
        user = make_user()
        db = query_side_effect(make_db(), {roleRequestDB: req, user: user})

        result = approve_role_request("req-1", db = db)

        assert result.status == "rejected"
        assert user.role == "guest"
        db.commit.assert_called_once()

    def test_approve_non_firefighter(self):
        req = make_request(role = "admin", status = "pending", firefighter_license_id = None)
        user = make_user()
        db = query_side_effect(make_db(), {roleRequestDB: req, user: user})

        result = approve_role_request("req-1", db = db)
        
        assert result.status == "approved"
        assert user.role == "admin"
        
    def test_approve_nonexistent_request(self):
        db = query_side_effect(make_db(), {roleRequestDB: Nine})

        with pytest.raises(HTTPException) as exc:
            approve_role_request("no-such-id", db = db)
        
        assert exc.value.status_code == 404

    def test_approved_already_approved(self):
        req = make_request(status = "approved")
        db = query_side_effect(make_db(), {roleRequestDB: req})

        with pytest.raises(HTTPException) as exc:
            approve_role_request("req-1", db = db)

        assert exc.value.status_code == 400

    def test_approved_already_rejected(self):
        req = make_request(status = "rejected")
        db = query_side_effect(make_db(), {roleRequestDB: req})

        with pytest.raises(HTTPException) as exc:
            approve_role_request("req-1", db = db)
        
        assert exc.value.status_code == 400

    def test_approve_with_no_matching_user(self):
        """User lookup returns none. Raise 404 instead of silent succeed"""
        req = make_request(role = "admin", status = "pending")
        db = query_side_effect(make_db(), {roleRequestDB: req, user: None})

        result = approve_role_request("req-1", db = db)

        assert result.status == "approved"

    @pytest.mark.parametrize("license_id", list(FIREFIGHTER_LICENSE_IDS))
    def test_all_valid_firefighter_licenses_accepted(self, license_id):
        req = make_request(role = "firefighter", status = "pending", firefighter_license_id = license_id)
        user = make_user()
        db = query_side_effect(make_db(), {roleRequestDB: req, user: user})

        result = approve_role_request("req-1", db = db)

        assert result.status == "approved"

# Test reject_role_request

class TestRejectRoleRequest:
    def test_reject_pending_request(self):
        req = make_request(status = "pending")
        db = query_side_effect(make_db(), {roleRequestDB: req})

        result = reject_role_request("req-1", db = db)

        assert result.status == "rejected"
        db.commit.assert_called_once()

    def test_reject_nonexistent(self):
        db = query_side_effect(make_db(), {roleRequestDB: None})

        with pytest.raises(HTTPException) as exc:
            reject_role_request("no-such-id", db = db)

        assert exc.value.status_code == 404

    def test_reject_already_processed(self):
        for already_done in ("approved", "rejected", "revoked"):
            req = make_request(status = already_done)
            db = query_side_effect(make_db(), {roleRequestDB: req})

            with pytest.raises(HTTPException) as exc:
                reject_role_request("req-1", db = db)
            
            assert exc.value.status_code == 400


# Test revoke_role_request

