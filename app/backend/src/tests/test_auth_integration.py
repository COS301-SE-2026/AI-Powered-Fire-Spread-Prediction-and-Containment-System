import pytest
from fastapi.testclient import TestClient

def test_register_success(client: TestClient, sample_user):
    response = client.post("/api/register", json=sample_user)
    assert response.status_code == 201
    assert response.json()["message"] == "User created successfully"

def test_register_duplicate_email(client: TestClient, sample_user):
    # First registration
    client.post("/api/register", json=sample_user)
    # Duplicate
    response = client.post("/api/register", json=sample_user)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_correct(client: TestClient, sample_user):
    client.post("/api/register", json=sample_user)
    response = client.post("/api/login", json={
        "email": sample_user["email"],
        "password": sample_user["password"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client: TestClient, sample_user):
    client.post("/api/register", json=sample_user)
    response = client.post("/api/login", json={
        "email": sample_user["email"],
        "password": "wrongpass"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_nonexistent_user(client: TestClient):
    response = client.post("/api/login", json={
        "email": "noone@example.com",
        "password": "pass"
    })
    assert response.status_code == 401