import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.models.reported_fires import FireReports
from app.backend.src.models.notification import Notification

from unittest.mock import patch

os.environ.setdefault("SKIP_DB_INIT", "1")
os.environ.setdefault("SKIP_SEED", "1")

from app.backend.src.dependencies.auth import hash_password
from app.backend.db import Base, get_db
from app.backend.main import app

# models for the firefighter dashboard
from app.backend.src.models.containment_lines import ContainmentLines
from app.backend.src.models.reported_fires import FireReports
from app.backend.src.models.role_request import RoleRequest
from app.backend.src.models.users import User

# seed data
from app.backend.seed import (
    REGIONAL_LOCATIONS as SEED_FIRE_REPORTS,
    SEED_USERS,
    seed_fire_reports,
)

TEST_DB_URL = os.getenv(
    "TEST_DB_URL", "postgresql://postgres:postgres@localhost:5433/test_fire_db"
)

engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Build db schema in test cluster before tests start"""
    with engine.begin() as conn:
        #  need for spacial columns
        conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS postgis;")

    Base.metadata.create_all(
        bind=engine,
        tables=[
            User.__table__,
            RoleRequest.__table__,
            FireReports.__table__,
            Notification.__table__,
            ContainmentLines.__table__,
        ],
    )
    yield

    Base.metadata.drop_all(
        bind=engine,
        tables=[
            User.__table__,
            RoleRequest.__table__,
            FireReports.__table__,
            Notification.__table__,
            ContainmentLines.__table__,
        ],
    )


@pytest.fixture(scope="function")
def db():
    """Provides test boundary using nested transact rollback"""
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    session.begin_nested()

    from sqlalchemy import event

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db):
    """Overrides FastAPI app db dependency use isolated test sess"""

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
        "licence_number": "LIC-001",
        "role": "user",
    }


def _split_full_name(full_name):
    parts = (full_name or "").strip().split(" ", 1)
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def make_user(db, full_name="Test User", email=None, role="user", lat=None, lng=None):
    user_email = email or f"user_{uuid.uuid4()}@example.com"
    name, surname = _split_full_name(full_name)
    user = User(
        id=str(uuid.uuid4()),
        email=user_email,
        hashed_password="test_password",
        name=name,
        surname=surname,
        id_number=str(uuid.uuid4().int)[:13],
        license_number=None,
        role=role,
        totp_secret=None,
        is_2fa_enabled=False,
    )
    if lat is not None and lng is not None:
        user.location_geom = f"SRID=4326;POINT({lng} {lat})"
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_role_request(db, user, role="firefighter", status="pending"):
    request = RoleRequest(
        request_id=str(uuid.uuid4()),
        user_id=user.id,
        requested_role=role,
        current_role=user.role,
        status=status,
        firefighter_license_id="LIC-001",
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def make_report(
    db,
    user=None,
    lat=-25.7479,
    lng=28.2293,
    status=ReportStatus.pending,
    status_index=1,
    reference_number=None,
    submitted_at=None,
    image_url="https://example.com/fire.jpg",
    photo_hash=None,
    description=None,
    boundary_radius=0.2,
):
    point_wkt = f"SRID=4326;POINT({lng} {lat})"
    report = FireReports(
        id=str(uuid.uuid4()),
        reference_number=f"FR-2026-{uuid.uuid4().hex[:6].upper()}",
        user_id=user.id if user else None,
        reporter_ip="127.0.0.1",
        location_text="Test location",
        description=description,
        image_url=image_url,
        photo_hash=photo_hash,
        location_geom=point_wkt,
        boundary_radius=boundary_radius,
        status=status,
        status_index=status_index,
        submitted_at=submitted_at or datetime.now(timezone.utc),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def seed_users_table(db):
    for data in SEED_USERS:
        user = User(
            id=data["id"],
            name=data["name"],
            surname=data["surname"],
            email=data["email"],
            id_number=data["id_number"],
            license_number=data["license_number"],
            hashed_password=hash_password(data["password"]),
            role=data["role"],
            is_active=True,
            is_2fa_enabled=False,
            totp_secret=None,
        )
        db.add(user)
    db.commit()


@pytest.fixture
def seeded_fire_reports(db):
    seed_users_table(db)
    seed_fire_reports(db)
    return db.query(FireReports).all()


@pytest.fixture
def small_grids():
    def _make(H=5, W=5):
        """Generate minimal synthetic grid data for testing physical model inputs.

        Creates uniform weather blowing east and flat terrain dictionaries along with an unburned status matrix of dimensions (H, W).

        Parameters
        ----------
        H : int, default 5
            Height of spatial grid in cells.
        W : int, default 5
            Width of spatial grid in cells.

        Returns
        -------
        weather : dict of {str: np.ndaray}
            Dictionary containing uniform meteorological arrays (`wind_u`, `wind_v`, `rel_humidity`, `temperature`)
        static : dict of {str: np.ndarray}
            Dictionary containing uniform terrain and fuel feature arrays (`elevation`, `slope`, `aspect_sin`, `aspect_cos`, `fuel_load`, `dryness`)
        burn : np.ndarray
            (H, W) array of zeros representing an initially unburned state matrix.
        """
        weather = {
            "wind_u": np.full((H, W), 3.0, np.float32),
            "wind_v": np.zeros((H, W), np.float32),
            "rel_humidity": np.full((H, W), 30.0, np.float32),
            "temperature": np.full((H, W), 25.0, np.float32),
        }
        static = {
            "elevation": np.full((H, W), 500.0, np.float32),
            "slope": np.zeros((H, W), np.float32),
            "aspect_sin": np.zeros((H, W), np.float32),
            "aspect_cos": np.ones((H, W), np.float32),
            "fuel_load": np.full((H, W), 0.8, np.float32),
            "dryness": np.full((H, W), 0.6, np.float32),
        }
        burn = np.zeros((H, W), np.int8)
        return weather, static, burn

    return _make


# for verification integration test cause we cant use env for mapbox token in deplyment
@pytest.fixture(autouse=True)
def mock_on_land():
    """prevent tests from depending on live mapbox API"""
    with patch(
        "app.backend.src.services.verification.rejection_checks.on_land",
        return_value=True,
    ):
        yield
