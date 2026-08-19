#This file is used to add new columns to the db if necessary

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
        conn.commit()