import pytest
from app.backend.main import app 
from app.backend.src.dependencies.auth import get_current_user 
from app.backend.src.enums.user_role import UserRole 
from app.backend.src.models.users import User

from app.backend.testing.integration.conftest import make_report, make_user

ME_URL = "/api/users/me"

SENSITIVE_FIELDS = {
    "hashed_password",
    "totp_secret",
    "reset_token",
    "reset_token_expires",   
    "id_number",
    "push_subscription",
}

def report_url(report_ref: str) -> str:
    return f"{ME_URL}/reported-fires/{report_ref}" 

# ----------------------------- helpers -----------------------------------
def reload_user(db, user_id: str) -> User:
    db.expire_all()
    return db.get(User, user_id)

def patch_me(client, **body):
    return client.patch(ME_URL, json=body)

@pytest.fixture
def me(db):
    return make_user(db, full_name="John Doe", email="john@example.com")
@pytest.fixture
def signed_in(client, me):
    app.dependency_overrides[get_current_user] = lambda: me
    yield me
    app.dependency_overrides.pop(get_current_user, None)

# ------------------------ Authentication -----------------------------
def test_get_me_without_token_returns_401(client):
    assert client.get (ME_URL).status_code == 401

def test_patch_me_without_token_returns_401(client):
    assert patch_me(client, name="Janet") .status_code == 401

def test_get_my_reported_fire_without_token_returns_401(client):
    assert client.get(report_url("any-ref")) .status_code == 401

# ----------------------- GET /api/users/me -----------------------------
def test_get_me_returns_current_user_profile(client, signed_in):
    response = client.get(ME_URL)

    assert response.status_code == 200
    body = response.json()
    assert (body["id"], body["name"], body["surname"], body["email"]) == (
        signed_in.id,
        "John",
        "Doe",
        "john@example.com"
    )

def test_get_me_response_excludes_sensitive_fields(client, signed_in):
    body = client.get(ME_URL).json()

    assert set(body).isdisjoint(SENSITIVE_FIELDS)

# ------------------------ PATCH /api/users/me ---------------------------------
def test_patch_me_valid_payload_returns_updated_profile(client, signed_in):
    response = patch_me(client, name="Jade", surname="Smith", email="jade@example.com")

    assert response.status_code == 200
    body = response.json()
    assert (body["name"], body["surname"], body["email"]) == (
        "Jade",
        "Smith",
        "jade@example.com",
    )

def test_patch_me_valid_payload_persists_to_database(client, db, signed_in):
    patch_me(client, name="Jade", surname="Smith", email="jade@example.com")

    stored = reload_user(db, signed_in.id)
    assert (stored.name, stored.surname, stored.email) == (
        "Jade",
        "Smith",
        "jade@example.com",
    )

def test_patch_me_partial_payload_leaves_other_fields_unchanged(client, db, signed_in):
    patch_me(client, name="Jade")

    stored = reload_user(db, signed_in.id)
    assert (stored.surname, stored.email) == ("Doe", "john@example.com") 
 
def test_patch_me_own_current_email_returns_200(client, signed_in):
    assert patch_me(client, email="jade@example.com").status_code == 200
 
 
def test_patch_me_email_is_stored_lowercase(client, db, signed_in):
    patch_me(client, email="NEW@Example.COM")
 
    assert reload_user(db, signed_in.id).email == "new@example.com"
 
 
def test_patch_me_surrounding_whitespace_is_trimmed(client, db, signed_in):
    patch_me(client, name="  Jade  ")
 
    assert reload_user(db, signed_in.id).name == "Jade"

# ------------------------------- emails --------------------------------------

def test_patch_me_email_taken_returns_409(client, db, signed_in):
    make_user(db, email="taken@example.com")
 
    response = patch_me(client, email="taken@example.com")
 
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already in use"
 
 
def test_patch_me_email_taken_in_different_case_returns_409(client, db, signed_in):
    make_user(db, email="Taken@Example.com")

    assert patch_me(client, email="taken@example.com").status_code == 409
 
def test_patch_me_email_taken_leaves_profile_unchanged(client, db, signed_in):
    make_user(db, email="taken@example.com")
 
    patch_me(client, name="Jade", email="taken@example.com")
 
    stored = reload_user(db, signed_in.id)
    assert (stored.name, stored.email) == ("John", "john@example.com")

# ------------------------ validation --------------------------------------------------

@pytest.mark.parametrize("bad_email", ["", "abc", "@example.com", "a b@example.com"])
def test_patch_me_invalid_email_returns_422(client, signed_in, bad_email):
    assert patch_me(client, email=bad_email).status_code == 422
 
 
@pytest.mark.parametrize("field", ["name", "surname"])
@pytest.mark.parametrize("blank", ["", "   "])
def test_patch_me_blank_field_leaves_value_unchanged(client, db, signed_in, field, blank):
    original = getattr(signed_in, field)
 
    patch_me(client, **{field: blank})
 
    assert getattr(reload_user(db, signed_in.id), field) == original
 
 
def test_patch_me_role_in_body_is_ignored(client, db, signed_in):
    patch_me(client, name="Janet", role="admin")
 
    assert reload_user(db, signed_in.id).role == UserRole.user

# ------------- GET /api/users/me/reported-fires/{report_ref}----------------------------------
def test_get_my_reported_fire_own_report_returns_200(client, db, signed_in):
    report = make_report(db, user=signed_in)

    response = client.get(report_url(report.reference_number))

    assert response.status_code == 200
    assert response.json()["id"] == str(report.id)
 
 
def test_get_my_reported_fire_other_users_report_returns_404(client, db, signed_in):
    other = make_user(db, email="other@example.com")
    report = make_report(db, user=other)
 
    assert client.get(report_url(report.id)).status_code == 404
 
 
def test_get_my_reported_fire_unknown_report_returns_404(client, signed_in):
    assert client.get(report_url("does-not-exist")).status_code == 404
 
 
def test_get_my_reported_fire_foreign_and_unknown_are_indistinguishable(
    client, db, signed_in
):
    other = make_user(db, email="other@example.com")
    foreign = client.get(report_url(make_report(db, user=other).id))
    missing = client.get(report_url("does-not-exist"))
 
    assert (foreign.status_code, foreign.json()) == (missing.status_code, missing.json())
 