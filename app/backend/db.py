import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    pool_size=90,
    max_overflow=35, # pool_size*max_overflow = 50 per worker
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Create all tables on startup."""
    from app.backend.src.models.containment_lines import ContainmentLines
    from app.backend.src.models.reported_fires import FireReports
    from app.backend.src.models.role_request import RoleRequest
    from app.backend.src.models.users import User
    from app.backend.src.models.notification import Notification

    Base.metadata.create_all(bind=engine)

    from app.backend.startup_migrations import run_startup_migrations

    run_startup_migrations(engine)