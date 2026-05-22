import sys
import os
import uuid

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["USE_SQLITE"] = "1"

from main import app
from db import init_db, get_db_connection

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()
    yield


@pytest.fixture(autouse=True)
def clear_users():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users")
        conn.commit()
    yield

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def sample_user():
    unique_email = f"testuser_{uuid.uuid4()}@example.com"
    return {
        "email": unique_email,
        "password": "test123",
        "name": "Test",
        "surname": "User",
        "id_number": "12345678",
        "licence_number": None,
        "role": "User"
    }