# import pytest
# import pyotp
# from fastapi.testclient import TestClient

# def test_setup_2fa(client: TestClient, sample_user):
#     client.post("/api/register", json=sample_user)
#     response = client.post(f"/auth/setup-2fa?username={sample_user['email']}")
#     assert response.status_code == 200
#     data = response.json()
#     assert "otpauth_url" in data
#     assert data["otpauth_url"].startswith("otpauth://totp/FireSpreadApp:")

# def test_login_with_2fa_enabled(client: TestClient, sample_user):
#     client.post("/api/register", json=sample_user)
#     setup_resp = client.post(f"/auth/setup-2fa?username={sample_user['email']}")
#     secret = pyotp.parse_uri(setup_resp.json()["otpauth_url"]).secret
#     totp = pyotp.TOTP(secret)
#     valid_code = totp.now()

#     login_resp = client.post("/api/login", json={
#         "email": sample_user["email"],
#         "password": sample_user["password"]
#     })
#     assert login_resp.status_code == 200
#     assert login_resp.json()["message"] == "2FA required"
#     assert "user_id" in login_resp.json()

#     verify_resp = client.post("/auth/verify-2fa", json={
#         "username": sample_user["email"],
#         "code": valid_code
#     })
#     assert verify_resp.status_code == 200
#     assert "access_token" in verify_resp.json()