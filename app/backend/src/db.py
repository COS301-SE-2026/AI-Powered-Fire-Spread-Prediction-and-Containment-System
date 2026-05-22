import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

_SQLITE_CONN = None


class SQLiteCursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, params=None):
        sql = query.replace("%s", "?")
        if params is None:
            params = ()
        return self._cursor.execute(sql, params)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self._cursor.close()
        return False


class SQLiteConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return SQLiteCursorWrapper(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self._conn.rollback()
        else:
            self._conn.commit()
        return False

def get_db_connection():
    use_sqlite = os.environ.get("USE_SQLITE", "0") == "1"
    if use_sqlite:
        global _SQLITE_CONN
        if _SQLITE_CONN is None:
            _SQLITE_CONN = sqlite3.connect(
                "file:fireaway_test?mode=memory&cache=shared",
                uri=True,
                check_same_thread=False,
            )
            _SQLITE_CONN.row_factory = sqlite3.Row
        return SQLiteConnectionWrapper(_SQLITE_CONN)

    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "postgres"),
        port=os.environ.get("DB_PORT", "5432"),
        database=os.environ.get("POSTGRES_DB", "fire_prediction"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", ""),
        cursor_factory=RealDictCursor,
    )

def init_db():
    """Create users table if it doesn't exist (with all columns)."""
    use_sqlite = os.environ.get("USE_SQLITE", "0") == "1"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if use_sqlite:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        hashed_password TEXT NOT NULL,
                        name TEXT,
                        surname TEXT,
                        id_number TEXT,
                        licence_number TEXT,
                        role TEXT DEFAULT 'User',
                        totp_secret TEXT,
                        is_2fa_enabled INTEGER DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
            else:
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