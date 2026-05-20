import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "postgres"),
        port=os.environ.get("DB_PORT", "5432"),
        database=os.environ.get("POSTGRES_DB", "fire_prediction"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", ""),
        cursor_factory=RealDictCursor
    )

def init_db():
    """Create users table if it doesn't exist (with all columns)."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    name TEXT,
                    surname TEXT,
                    id_number TEXT,
                    licence_number TEXT,
                    role TEXT DEFAULT 'User',
                    totp_secret TEXT,
                    is_2fa_enabled BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            """)
        conn.commit()