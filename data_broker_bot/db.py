import sqlite3
from typing import Dict, List, Optional
from data_broker_bot.models import User


class Database:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._shared_conn: Optional[sqlite3.Connection] = None
        if self.db_path == ":memory:":
            # Use a persistent connection for in-memory database
            self._shared_conn = sqlite3.connect(":memory:")
            self._shared_conn.row_factory = sqlite3.Row
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self._shared_conn is not None:
            return self._shared_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        conn = self._get_connection()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                phone TEXT,
                cpf TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        if self._shared_conn is None:
            conn.close()

    def save_user(self, user: User) -> None:
        """Save user record to database. PII fields in user.pii_fields are ciphertext."""
        conn = self._get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO users (user_id, name, email, phone, cpf)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user.user_id,
                    user.pii_fields.get("name"),
                    user.pii_fields.get("email"),
                    user.pii_fields.get("phone"),
                    user.pii_fields.get("cpf"),
                ),
            )
            conn.commit()
        finally:
            if self._shared_conn is None:
                conn.close()

    def get_user(self, user_id: str) -> Optional[User]:
        """Fetch user record from database. PII fields remain encrypted."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT user_id, name, email, phone, cpf, created_at FROM users WHERE user_id = ?",
                (user_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return User(
                user_id=row["user_id"],
                pii_fields={
                    "name": row["name"],
                    "email": row["email"],
                    "phone": row["phone"],
                    "cpf": row["cpf"],
                },
                created_at=row["created_at"],
            )
        finally:
            if self._shared_conn is None:
                conn.close()

    def list_users(self) -> List[User]:
        """List all users with encrypted PII fields."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT user_id, name, email, phone, cpf, created_at FROM users")
            rows = cur.fetchall()
            return [
                User(
                    user_id=row["user_id"],
                    pii_fields={
                        "name": row["name"],
                        "email": row["email"],
                        "phone": row["phone"],
                        "cpf": row["cpf"],
                    },
                    created_at=row["created_at"],
                )
                for row in rows
            ]
        finally:
            if self._shared_conn is None:
                conn.close()

    def update_user_pii(self, user_id: str, pii_fields: Dict[str, Optional[str]]) -> None:
        """Update PII fields for a specific user."""
        conn = self._get_connection()
        try:
            conn.execute(
                """
                UPDATE users
                SET name = ?, email = ?, phone = ?, cpf = ?
                WHERE user_id = ?
                """,
                (
                    pii_fields.get("name"),
                    pii_fields.get("email"),
                    pii_fields.get("phone"),
                    pii_fields.get("cpf"),
                    user_id,
                ),
            )
            conn.commit()
        finally:
            if self._shared_conn is None:
                conn.close()

    def dump_db(self) -> List[Dict[str, Optional[str]]]:
        """Return raw database rows as a list of dicts to demonstrate ciphertext storage."""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT user_id, name, email, phone, cpf, created_at FROM users")
            return [dict(row) for row in cur.fetchall()]
        finally:
            if self._shared_conn is None:
                conn.close()

    def close(self) -> None:
        if self._shared_conn:
            self._shared_conn.close()
            self._shared_conn = None
