import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables on startup."""
    from models.containment_lines import ContainmentLines
    from models.reported_fires import FireReports
    from models.role_request import RoleRequest
    from models.users import User
    from models.notification import Notification

    Base.metadata.create_all(bind=engine)

    from startup_migrations import run_startup_migrations

    run_startup_migrations(engine)
