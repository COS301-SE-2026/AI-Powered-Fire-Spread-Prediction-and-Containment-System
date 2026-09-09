# This file is used to add new columns to the db if necessary

from sqlalchemy import text
from sqlalchemy.engine import Engine


def run_startup_migrations(engine: Engine) -> None:
    with engine.connect() as conn:
        conn.execute(
            text(
                """
                ALTER TABLE users ADD COLUMN IF NOT EXISTS location_geom geometry(Point, 4326);
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_users_location_geom ON users USING GIST (location_geom);
                """
            )
        )
        # for fire report verification
        conn.execute(
            text(
                """
                ALTER TABLE fire_reports ADD COLUMN IF NOT EXISTS priority VARCHAR NOT NULL DEFAULT 'normal';
                """
            )
        )
        conn.execute(
            text(
                """
                ALTER TABLE fire_reports ADD COLUMN IF NOT EXISTS system_verified BOOLEAN NOT NULL DEFAULT false;
                """
            )
        )
        conn.execute(
            text(
                """
                ALTER TABLE fire_reports ADD COLUMN IF NOT EXISTS verification_notes TEXT;
                """
            )
        )
        conn.execute(
            text(
                """
                ALTER TABLE fire_reports ADD COLUMN IF NOT EXISTS photo_hash VARCHAR(64);
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_fire_reports_photo_hash ON fire_reports (photo_hash);
                """))
        conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_fire_reports_submitted_at ON fire_reports (submitted_at DESC);
                """))
        conn.commit()