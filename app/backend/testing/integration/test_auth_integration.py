import pytest
from fastapi.testclient import TestClient


def test_register_success(client: TestClient, sample_user):
    response = client.post("/api/auth/register", json=sample_user)
    assert response.status_code == 201
    body = response.json()

    assert body["requires_2fa"] is True
    assert body["email"] == sample_user["email"]
    assert "otpauth_url" in body

def test_login_wrong_password(client: TestClient, sample_user):
    client.post("/api/auth/register", json=sample_user)
    response = client.post(
        "/api/auth/login", json={"email": sample_user["email"], "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_nonexistent_user(client: TestClient):
    response = client.post(
        "/api/auth/login", json={"email": "noone@example.com", "password": "pass"}
    )
    assert response.status_code == 401

