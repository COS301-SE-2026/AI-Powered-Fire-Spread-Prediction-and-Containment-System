import os
import sys
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ.setdefault("SKIP_DB_INIT", "1")
os.environ.setdefault("SKIP_SEED", "1")

from db import Base, get_db
from models import User, RoleRequestDB
from main import app

engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine, tables=[User.__table__, RoleRequestDB.__table__])
    yield
    Base.metadata.drop_all(bind=engine, tables=[User.__table__, RoleRequestDB.__table__])


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


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
        "role": "User",
    }


def _split_full_name(full_name):
    parts = (full_name or "").strip().split(" ", 1)
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def make_user(db, full_name="Test User", email=None, role="User"):
    user_email = email or f"user_{uuid.uuid4()}@example.com"
    name, surname = _split_full_name(full_name)
    user = User(
        id=str(uuid.uuid4()),
        email=user_email,
        hashed_password="test_password",
        name=name,
        surname=surname,
        id_number="12345678",
        license_number=None,
        role=role,
        totp_secret=None,
        is_2fa_enabled=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_role_request(db, user, role="firefighter", status="pending", license_id=None, email=None, full_name=None):
    user_email = email or user.email
    user_full_name = full_name or " ".join(filter(None, [user.name, user.surname])).strip()
    effective_license_id = license_id
    if role == "firefighter" and effective_license_id is None:
        effective_license_id = "FF-1001"
    request = RoleRequestDB(
        user_id=user.id,
        user_full_name=user_full_name,
        email=user_email,
        role=role,
        status=status,
        firefighter_license_id=effective_license_id,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request