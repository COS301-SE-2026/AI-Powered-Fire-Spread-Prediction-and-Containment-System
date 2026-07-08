import pytest
from fastapi.testclient import TestClient

def test_register_success(client: TestClient, sample_user):
    response = client.post("/api/auth/register", json=sample_user)
    assert response.status_code == 201
    assert response.json()["message"] == "User succefully registered"

def test_register_duplicate_email(client: TestClient, sample_user):
    client.post("/api/auth/register", json=sample_user)
    response = client.post("/api/auth/register", json=sample_user)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists please enter a valid email."

def test_login_correct(client: TestClient, sample_user):
    client.post("/api/auth/register", json=sample_user)
    response = client.post("/api/auth/login", json={
        "email": sample_user["email"],
        "password": sample_user["password"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client: TestClient, sample_user):
    client.post("/api/auth/register", json=sample_user)
    response = client.post("/api/auth/login", json={
        "email": sample_user["email"],
        "password": "wrongpass"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Password is incorrect please try again"

def test_login_nonexistent_user(client: TestClient):
    response = client.post("/api/auth/login", json={
        "email": "noone@example.com",
        "password": "pass"
    })
    assert response.status_code == 401