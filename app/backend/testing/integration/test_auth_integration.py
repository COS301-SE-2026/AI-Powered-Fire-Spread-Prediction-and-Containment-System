# import pytest
# from fastapi.testclient import TestClient


# def test_register_success(client: TestClient, sample_user):
#     response = client.post("/api/auth/register", json=sample_user)
#     assert response.status_code == 201
#     body = response.json()

#     assert body["requires_2fa"] is True
#     assert body["email"] == sample_user["email"]
#     assert "otpauth_url" in body


# def test_register_duplicate_email(client: TestClient, sample_user):
#     client.post("/api/auth/register", json=sample_user)
#     response = client.post("/api/auth/register", json=sample_user)
#     assert response.status_code == 400
#     assert (
#         response.json()["detail"] == "Email already exists please enter a valid email."
#     )


# def test_login_correct(client: TestClient, sample_user):
#     client.post("/api/auth/register", json=sample_user)
#     response = client.post(
#         "/api/auth/login",
#         json={"email": sample_user["email"], "password": sample_user["password"]},
#     )

#     body = response.json()

#     assert response.status_code == 200
#     assert body["requires_2fa"] is True
#     assert body["email"] == sample_user["email"]
#     assert "otpauth_url" is not None


# def test_login_wrong_password(client: TestClient, sample_user):
#     client.post("/api/auth/register", json=sample_user)
#     response = client.post(
#         "/api/auth/login", json={"email": sample_user["email"], "password": "wrongpass"}
#     )
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Password is incorrect please try again"


# def test_login_nonexistent_user(client: TestClient):
#     response = client.post(
#         "/api/auth/login", json={"email": "noone@example.com", "password": "pass"}
#     )
#     assert response.status_code == 401
