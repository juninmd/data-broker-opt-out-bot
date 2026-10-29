from fastapi import Request, HTTPException, status, Depends, Cookie
from typing import Optional
import os
from src.db.database import (
    create_otp_token,
    verify_and_use_otp_token,
    create_session,
    validate_session,
)

COOKIE_NAME = "dashboard_session"

def generate_otp_link(base_url: str = "http://localhost:8000", db_path: str = None) -> str:
    token = create_otp_token(db_path=db_path)
    return f"{base_url.rstrip('/')}/auth/login?token={token}"

def get_current_session(request: Request, db_path: str = None) -> Optional[str]:
    session_id = request.cookies.get(COOKIE_NAME)
    if not session_id:
        return None
    if validate_session(session_id, db_path=db_path):
        return session_id
    return None

def require_auth(request: Request):
    # Zero-config single-user deploy behavior:
    # If DISABLE_AUTH is explicitly set to true (e.g. for dev/testing), skip auth check
    if os.environ.get("DISABLE_AUTH", "").lower() in ("true", "1", "yes"):
        return True

    session_id = request.cookies.get(COOKIE_NAME)
    if not session_id or not validate_session(session_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized. Please request a login link via Telegram."
        )
    return True
