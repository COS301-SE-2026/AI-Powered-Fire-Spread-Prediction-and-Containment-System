import pyotp
from fastapi.testclient import TestClient


def test_register_returns_2fa_setup(client: TestClient, sample_user):
    """Registration now includes the TOTP setup (there is no /setup-2fa step)."""
    response = client.post("/api/auth/register", json=sample_user)
    assert response.status_code == 201

    data = response.json()
    assert data["requires_2fa"] is True
    secret = pyotp.parse_uri(data["otpauth_url"]).secret
    assert len(pyotp.TOTP(secret).now()) == 6


def test_login_with_2fa_enabled(client: TestClient, make_registered_user):
    creds, secret = make_registered_user(enable_2fa=True)

    login_resp = client.post(
        "/api/auth/login",
        json={"email": creds["email"], "password": creds["password"]},
        )
    assert login_resp.status_code == 200
    body = login_resp.json()
    assert body["requires_2fa"] is True
    assert body["email"] == creds["email"]
    assert "access_token" not in body
    verify_resp = client.post(
        "/api/auth/verify-2fa",
        json={"username": creds["email"], "code": pyotp.TOTP(secret).now()},
    )
    assert verify_resp.status_code == 200


def test_verify_2fa_wrong_code(client: TestClient, make_registered_user):
    creds, _ = make_registered_user(enable_2fa=True)

    response = client.post(
        "/api/auth/verify-2fa",
        json={"username": creds["email"], "code": "000000"},
    )
    # ASSUMPTION: 400 or 401; tighten once you confirm which one
    assert response.status_code in (400, 401)
    assert "access_token" not in response.json()


def test_verify_2fa_unknown_user(client: TestClient):
    response = client.post(
        "/api/auth/verify-2fa",
        json={"username": "noone@example.com", "code": "123456"},
    )
    assert response.status_code in (400, 401, 404)
    assert "access_token" not in response.json()