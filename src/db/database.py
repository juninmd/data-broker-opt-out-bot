import os
import sqlite3
import secrets
from datetime import datetime, timedelta, timezone

def get_db_path(db_path: str = None) -> str:
    return db_path or os.environ.get("DATABASE_PATH", "app.db")

def get_db(db_path: str = None) -> sqlite3.Connection:
    path = get_db_path(db_path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = None) -> None:
    path = get_db_path(db_path)
    with get_db(path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                broker_name TEXT NOT NULL,
                request_type TEXT NOT NULL DEFAULT 'opt-out',
                status TEXT NOT NULL DEFAULT 'PENDING',
                details TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS broker_health (
                broker_name TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'HEALTHY',
                response_time_ms INTEGER DEFAULT 0,
                last_check TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otp_tokens (
                token TEXT PRIMARY KEY,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                expires_at TEXT NOT NULL,
                used INTEGER NOT NULL DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                expires_at TEXT NOT NULL
            )
        """)
        conn.commit()

def add_request(broker_name: str, request_type: str = "opt-out", status: str = "PENDING", details: str = "", db_path: str = None) -> int:
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute(
            "INSERT INTO requests (broker_name, request_type, status, details, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (broker_name, request_type, status, details, now, now)
        )
        conn.commit()
        return cursor.lastrowid

def get_requests(limit: int = 100, db_path: str = None):
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM requests ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]

def update_broker_health(broker_name: str, status: str, response_time_ms: int = 0, db_path: str = None):
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
            INSERT INTO broker_health (broker_name, status, response_time_ms, last_check)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(broker_name) DO UPDATE SET
                status = excluded.status,
                response_time_ms = excluded.response_time_ms,
                last_check = excluded.last_check
        """, (broker_name, status, response_time_ms, now))
        conn.commit()

def get_broker_health(db_path: str = None):
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM broker_health ORDER BY broker_name ASC")
        return [dict(row) for row in cursor.fetchall()]

def create_otp_token(expires_in_minutes: int = 10, db_path: str = None) -> str:
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = (now + timedelta(minutes=expires_in_minutes)).isoformat()
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO otp_tokens (token, created_at, expires_at, used) VALUES (?, ?, ?, 0)",
            (token, now.isoformat(), expires_at)
        )
        conn.commit()
    return token

def verify_and_use_otp_token(token: str, db_path: str = None) -> bool:
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM otp_tokens WHERE token = ?", (token,))
        row = cursor.fetchone()
        if not row:
            return False
        token_data = dict(row)
        if token_data["used"] != 0:
            return False
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            return False
        cursor.execute("UPDATE otp_tokens SET used = 1 WHERE token = ?", (token,))
        conn.commit()
        return True

def create_session(db_path: str = None, expires_in_hours: int = 24) -> str:
    session_id = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = (now + timedelta(hours=expires_in_hours)).isoformat()
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (session_id, created_at, expires_at) VALUES (?, ?, ?)",
            (session_id, now.isoformat(), expires_at)
        )
        conn.commit()
    return session_id

def validate_session(session_id: str, db_path: str = None) -> bool:
    if not session_id:
        return False
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            return False
        session_data = dict(row)
        expires_at = datetime.fromisoformat(session_data["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            return False
        return True
