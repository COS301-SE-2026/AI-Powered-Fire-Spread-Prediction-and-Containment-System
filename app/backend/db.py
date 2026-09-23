import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=5, # pool_size*max_overflow = 50 per worker
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


BASELINE_REVISION = "7db2f82cc86f"

def migrate_db():
    """
    Apply pending alembic migrations
    """

    cfg = Config(str(Path(__file__).parent / "alembic.ini"))
    with engine.begin() as conn:
        conn.execute(
            text(
                "SELECT pg_advisory_xact_lock(472019)"
            )
        )
        cfg.attributes["connection"] = conn
        insp = inspect(conn)
        if not insp.has_table("alembic_version") and insp.has_table("users"):
            command.stamp(cfg, BASELINE_REVISION)
        command.upgrade(cfg, "head")