from types import SimpleNamespace 
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from pydantic import ValidationError 
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.backend.src.dependencies.auth import get_current_user 
from app.backend.src.routes.users import profile as routes 
from app.backend.src.schemas.user import UserResponse, UserUpdate 
from app.backend.src.services.users import profile as service

SERVICE_PATCH = "profile_service"
REPORTS_PATCH = "fire_report"

SENSITIVE_FIELDS = {
    "hashed_password",
    "totp_secret",
    "reset_token",
    "reset_token_expires",
    "id_number",
    "push_subscription",
}

EXPECTED_ENDPOINTS = {
    ("GET", '/api/users/me'),
    ("PATCH", "/api/users/me"),
    ("GET", "/api/users/me/reported-fires/{report_ref}"),
}

def make_db(existing=None) -> MagicMock:
    """Mock db with unique email"""
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = existing
    return db 

@pytest.fixture
def user() -> SimpleNamespace:
    return SimpleNamespace(
        id="user-1",
        name="John",
        surname="Doe",
        email="john@example.com",
        role="user",
    )

@pytest.fixture
def db() -> MagicMock:
    return make_db()

#------------------------------ email ------------------------------

def test_update_profile_new_updates_email(user, db):
    service.update_profile(UserUpdate(email="new@example.com"), db, user)

    assert user.email == "new@example.com"

def test_update_profile_email_taken_raises_409(user):
    with pytest.raises(HTTPException) as error:
        service.update_profile(
            UserUpdate(email="taken@example.com"), make_db(existing=object()), user
        )

    assert error.value.status_code == 409
    assert error.value.detail == "Email already in use"

def test_update_profile_email_taken_leaves_email_unchanged(user):
    with pytest.raises(HTTPException):
        service.update_profile(
            UserUpdate(email="taken@example.com"), make_db(existing=object()), user
        )

    assert user.email == "john@example.com"

def test_update_profile_email_taken_does_not_commit(user):
    db = make_db(existing=object())

    with pytest.raises(HTTPException):
        service.update_profile(UserUpdate(email="taken@example.com"), db, user)

    db.commit.assert_not_called()

def test_profile_email_taken_applies_not_partial_changes(user):
    """ rejected email shouldnt leave half changed things in fields """
    before = dict(vars(user))

    with pytest.raises(HTTPException):
        service.update_profile(
            UserUpdate(name="Jade", surname="Smith", email="taken@example.com"),
            make_db(existing=object()),
            user,
        )

    assert vars(user) == before 

def test_update_profile_same_email_skips_uniqueness(user, db):
    service.update_profile(UserUpdate(email="john@example.com"), db, user)
 
    db.query.assert_not_called()

def test_profile_no_email_skips_uniqueness(user, db):
    service.update_profile(UserUpdate(name="John"), db, user)
 
    db.query.assert_not_called()

def test_update_profile_none_email_leaves_email_unchanged(user, db):
    service.update_profile(UserUpdate(email=None), db, user)

    assert user.email == "john@example.com"

def test_user_update_empty_email_is_rejected():
    with pytest.raises(ValidationError):
        UserUpdate(email="")

def test_update_profile_email_mixed_case_is_stored_lowercase(user, db):
    service.update_profile(UserUpdate(email="NEW@Example.COM"), db, user)
 
    assert user.email == "new@example.com"

def test_update_profile_same_email_different_case_skips_lookup(user, db):
    service.update_profile(UserUpdate(email="JOHN@example.com"), db, user)

    db.query.assert_not_called()

# ------------------------------ name and surname ------------------------------

@pytest.mark.parametrize("field", ["name", "surname"])
def test_update_profile_field_provided_updates_user(user, db, field):
    service.update_profile(UserUpdate(**{field: "Updated"}), db, user)
    
    assert getattr(user, field) == "Updated"

@pytest.mark.parametrize("field", ["name", "surname"])
@pytest.mark.parametrize("empty_value", [None, ""])
def test_update_profile_field_empty_leaves_user_unchanged(user, db, field, empty_value):
    original = getattr (user, field)
    
    service. update_profile(UserUpdate(**{field: empty_value}), db, user)
    
    assert getattr(user, field) == original

@pytest.mark.parametrize("field", ["name", "surname"])
@pytest.mark.parametrize("blank", ["", "\t\n"])
def test_update_profile_field_whitespace_only_leaves_user_unchanged(
    user, db, field, blank
):
    original = getattr(user, field)
   
    service.update_profile(UserUpdate(**{field: blank}), db, user)
    
    assert getattr(user, field) == original

@pytest.mark.parametrize("field", ["name", "surname"])
def test_update_profile_field_surrounding_whitespace_is_trimmed(user, db, field):
    service.update_profile(UserUpdate(**{field: " Jade "}), db, user)

    assert getattr(user, field) == "Jade"

def test_update_profile_all_fields_updates_every_field(user, db):
    payload = UserUpdate(name="Jade", surname="Smith", email="jade@example.com")

    service.update_profile(payload, db, user)

    assert (user.name, user.surname, user.email) == (
        "Jade",
        "Smith",
        "jade@example.com"
    )

def test_update_profile_empty_payload_changes_nothing(user, db):
    before = dict(vars(user))

    service.update_profile(UserUpdate(), db, user)

    assert vars(user) == before

def test_update_profile_role_in_payload_is_ignored(user, db):
    service.update_profile(UserUpdate(name="Jade", role="admin"), db, user)
 
    assert user.role == "user"

# ---------------------------- persistence ------------------------------
def test_update_profile_valid_payload_commits_once(user, db):
    service.update_profile(UserUpdate(name="Jade"), db, user)
    
    db.commit.assert_called_once()

def test_update_profile_valid_payload_refreshes_user(user, db):
    service.update_profile(UserUpdate(name="Jade"), db, user)
    
    db.refresh.assert_called_once_with(user)

def test_update_profile_commits_before_refreshing(user, db):
    service.update_profile(UserUpdate(name="Jade"), db, user)
    
    assert [call[0] for call in db.method_calls] == ["commit", "refresh"]

def test_update_profile_valid_payload_returns_current_user(user, db):
    result = service.update_profile(UserUpdate(name="Jade"), db, user)
    
    assert result is user

def test_update_profile_commit_failure_propagates_error(user, db):
    db.commit.side_effect = SQLAlchemyError("connection lost")
    
    with pytest.raises(SQLAlchemyError):
        service.update_profile(UserUpdate(name="Jade"), db, user)

def test_update_profile_commit_failure_does_not_refresh(user, db) :
    db.commit.side_effect = SQLAlchemyError("connection lost")
    
    with pytest.raises(SQLAlchemyError):
        service.update_profile(UserUpdate(name= "Jade"), db, user)
    
    db.refresh.assert_not_called()

def test_update_profile_commit_failure_rolls_back_session(user, db):
    db.commit.side_effect = SQLAlchemyError("connection lost")
    
    with pytest.raises(SQLAlchemyError):
        service.update_profile(UserUpdate(name="Jade"), db, user)
    
    db.rollback.assert_called_once()

def test_update_profile_commit_integrity_error_raises_409(user, db):
    db.commit.side_effect = IntegrityError("UPDATE", {}, Exception("duplicate key"))

    with pytest.raises(HTTPException) as error:
        service.update_profile(UserUpdate(email="race@example.com"), db, user)

    assert error.value.status_code == 409

def test_update_profile_commit_integrity_error_rolls_back_session(user, db):
    db.commit.side_effect = IntegrityError("UPDATE", {}, Exception("duplicate key"))
 
    with pytest.raises((HTTPException, IntegrityError)):
        service.update_profile(UserUpdate(email="race@example.com"), db, user)
 
    db.rollback.assert_called_once()

# ------------------------------ routes -----------------------------

# ----------------------------- GET / me ------------------------------
def test_get_my_profile_returns_current_user(user):
    assert routes.get_my_profile(current_user=user) is user

# ----------------------------- PATCH / me ------------------------------
@patch.object(routes, SERVICE_PATCH)
def test_update_my_profile_passes_payload_db_and_user_to_service(mock_service, user):
    payload, db = UserUpdate(name="Jade"), MagicMock()
    
    routes.update_my_profile(payload=payload, db=db, current_user=user)
    
    mock_service.update_profile.assert_called_once_with(payload, db, user)

@patch.object(routes, SERVICE_PATCH)
def test_update_my_profile_returns_service_result(mock_service, user):
    result = routes.update_my_profile(
        payload=UserUpdate(), db=MagicMock(), current_user=user
    )

    assert result is mock_service. update_profile.return_value

@patch.object(routes, SERVICE_PATCH)
def test_update_my_profile_service_http_error_propagates(mock_service, user):
    mock_service.update_profile.side_effect = HTTPException(
        status_code=409, detail="Email already in use"
    )

    with pytest.raises(HTTPException) as error:
        routes.update_my_profile(
            payload=UserUpdate(email="x@example.com"), db=MagicMock(), current_user=user
        )

    assert error.value.status_code == 409

# ------------------------- GET /me/reported-fires/{report_ref} ------------------------------
@patch.object (routes, REPORTS_PATCH)
def test_get_my_reported_fires_own_report_returns_report(mock_reports, user):
    report = {"id": "rep-1", "user_id": "user-1"}
    mock_reports.get_fire_report_by_id.return_value = report
    
    result = routes.get_my_reported_fires (
        report_ref="rep-1", db=MagicMock(), current_user=user
    )

    assert result is report

@patch.object (routes, REPORTS_PATCH)
def test_get_my_reported_fires_looks_up_by_ref_and_db(mock_reports, user):
    db = MagicMock()
    mock_reports.get_fire_report_by_id.return_value = {"user_id": "user-1"}
    
    routes.get_my_reported_fires(report_ref="rep-1", db=db, current_user=user)
    
    mock_reports.get_fire_report_by_id.assert_called_once_with("rep-1", db)

@patch.object (routes, REPORTS_PATCH)
def test_get_my_reported_fires_unknown_report_raises_404(mock_reports, user):
    mock_reports.get_fire_report_by_id.side_effect = ValueError("missing")
    
    with pytest.raises(HTTPException) as error:
        routes.get_my_reported_fires(
            report_ref="nope", db=MagicMock(), current_user=user
        )
        
    assert error.value.status_code == 404

@patch.object (routes, REPORTS_PATCH)
def test_get_my_reported_fires_other_users_report_raises_404(mock_reports, user):
    mock_reports.get_fire_report_by_id.return_value = {"user_id": "someone-else"}
    
    with pytest.raises(HTTPException) as error:
        routes.get_my_reported_fires(
            report_ref="rep-1", db=MagicMock(), current_user=user
        )

    assert error.value.status_code == 404

@patch.object(routes, REPORTS_PATCH)
def test_get_my_reported_fires_missing_and_foreign_are_indistinguishable(
    mock_reports, user
):
    errors = []
    for outcome in (ValueError("missing"), {"user_id": "someone-else"}):
        if isinstance(outcome, Exception):
            mock_reports.get_fire_report_by_id.side_effect = outcome
        else:
            mock_reports.get_fire_report_by_id.side_effect = None
            mock_reports.get_fire_report_by_id.return_value = outcome
        with pytest.raises(HTTPException) as error:
            routes.get_my_reported_fires(
                report_ref="rep-1", db=MagicMock(), current_user=user
            )
        errors.append((error.value.status_code, error.value.detail))
        
    assert errors[0] == errors[1]

@patch.object (routes, REPORTS_PATCH)
def test_get_my_reported_fires_unexpected_error_is_not_masked_as_404(
    mock_reports, user
):
    mock_reports.get_fire_report_by_id.side_effect = RuntimeError("db down")
    
    with pytest.raises(RuntimeError):
        routes.get_my_reported_fires(
            report_ref="rep-1", db=MagicMock(), current_user=user
        )

@patch.object (routes, REPORTS_PATCH)
def test_get_my_reported_fires_report_without_user_id_raises_404(
    mock_reports, user
):
    mock_reports.get_fire_report_by_id.return_value = {"id": "rep-1"}
    
    with pytest.raises(HTTPException) as error:
        routes.get_my_reported_fires(
            report_ref="rep-1", db=MagicMock(), current_user=user
        )

    assert error.value.status_code == 404

