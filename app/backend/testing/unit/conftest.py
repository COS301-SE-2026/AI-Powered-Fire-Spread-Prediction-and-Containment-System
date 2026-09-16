import os
import uuid
import itertools

from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env.test")

import numpy as np
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.backend.src.models.users import User
from app.backend.src.models.reported_fires import FireReports
from app.backend.src.models.notification import Notification
from app.backend.src.models.containment_lines import ContainmentLines
from app.backend.src.models.role_request import RoleRequest

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


# --------Fixtures for admin role request approval---------------
from app.backend.db import Base
from app.backend.src.enums.role_request_status import RequestStatus
from app.backend.src.enums.user_role import UserRole

ADMIN_ID = "admin-1"

id_num_seq = itertools.count(1)

def fake_id_number():
    return f"{next(id_num_seq):013d}"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(os.environ["TEST_DATABASE_URL"])
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()
    
@pytest.fixture()
def db_session(engine):
    """
    Each test runs inside its own transaction, rolled back at the end -
    fast, isolated, and doesn't require recreating the schema per test.
    """
    connection = engine.connect()
    outer_transaction = connection.begin()
    session = sessionmaker(bind=connection, autoflush=False, autocommit=False)()
    try:
        yield session
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()
        
@pytest.fixture()
def admin_id(db_session):
    """
    A real admin User row. reviewed_by is a FK to users.id, so a base string
    with no matching row fails againts postgres
    """
    admin = User(id=ADMIN_ID, name="Ada", surname="Admin", email="admin@example.com", id_number=fake_id_number(), role=UserRole.admin)
    db_session.add(admin)
    db_session.commit()
    return admin.id

@pytest.fixture()
def scenario(db_session, admin_id):
    """
    Factory for building (admin_is, user, role_request) trio.
    
    Usage:
        admin_id, user, req = scenario()
        admin_id, user, req = scenario(status=RequestStatus.approved)
        admin_id, user, request = scenario(orphan=True) # user row doesn't exist
    """
    
    def make(status=RequestStatus.pending, requested_role=UserRole.admin, current_role=UserRole.user, orphan=False):
        if orphan:
            db_session.execute(text("ALTER TABLE role_requests DISABLE TRIGGER ALL"))
            req = RoleRequest(
                request_id=str(uuid.uuid4()),
                user_id="nonexistent-user",
                requested_role=requested_role,
                current_role=current_role,
                status=status,
            )
            db_session.add(req)
            db_session.commit()
            db_session.execute(text("ALTER TABLE role_requests ENABLE TRIGGER ALL"))
            db_session.commit()
            return admin_id, None, req
        
        user = User(
            id=str(uuid.uuid4()),
            name="Jane",
            surname="Doe",
            email=f"{uuid.uuid4()}@example.com",
            id_number=fake_id_number(),
            role=current_role,
        )
        db_session.add(user)
        db_session.commit()
        
        req = RoleRequest(
            request_id=str(uuid.uuid4()),
            user_id=user.id,
            requested_role=requested_role,
            current_role=current_role,
            status=status,
        )
        db_session.add(req)
        db_session.commit()
        db_session.refresh(req)
        return admin_id, user, req
    
    return make
            