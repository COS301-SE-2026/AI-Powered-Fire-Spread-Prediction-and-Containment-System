import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
import pytest
from fastapi.testclient import TestClient
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from main import app

TEST_DB_NAME = "test_fire_db"
os.environ["POSTGRES_DB"] = TEST_DB_NAME

try:
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST", "postgres"),
        user=os.environ.get("POSTGRES_USER", "myuser"),
        password=os.environ.get("POSTGRES_PASSWORD", "mypassword"),
        database="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'")
    if not cur.fetchone():
        cur.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Warning: Could not create test database: {e}")

from db import init_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()
    yield

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def sample_user():
    unique_email = f"testuser_{int(time.time())}@example.com"
    return {
        "email": unique_email,
        "password": "test123",
        "name": "Test",
        "surname": "User",
        "id_number": "12345678",
        "licence_number": None,
        "role": "User"
    }