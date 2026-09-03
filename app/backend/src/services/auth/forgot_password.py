
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
 
from sqlalchemy.orm import Session
 
from dependencies.auth import hash_password
from models.users import User
from schemas.auth import ResetPasswordRequest
from services.auth.email import send_password_reset_email
from services.auth.login import valkey_client

RESET_TOKEN_TTL_MINUTES = 15
RESET_REQUEST_LIMIT = 3
RESET_REQUEST_WINDOW_SECONDS = 60 * 60  # 1 hour
MIN_PASSWORD_LENGTH = 8

GENERIC_MESSAGE = (
    "If an account with that email exists, we've sent a password reset link."
)

def _hash_token(token: str) -> str:
    """Hash the token using SHA256."""
    return hashlib.sha256(token.encode()).hexdigest()

def _rate_limit_key(email: str)-> str:
    return f"auth:reset-request:{email}"

def request_password_reset(db: Session, email: str) -> Optional[Tuple[str, str]]:
    email_key = email.strip().lower()
    rl_key = _rate_limit_key(email_key)
    attempts = valkey_client.incr(rl_key)
    if attempts == 1:
        valkey_client.expire(rl_key, RESET_REQUEST_WINDOW_SECONDS)
    if attempts > RESET_REQUEST_LIMIT:
        return None

    raw_token = secrets.token_urlsafe(32)
    user.reset_token = _hash_token(raw_token)
    user.reset_token_expires = datetime.now(timezone.utc) + timedelta(
        minutes=RESET_TOKEN_TTL_MINUTES
    )
    db.commit()

    return user.email, raw_token

def reset_password(db: Session, request: ResetPasswordRequest) -> None:
    if len(request.new_password) < MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
        )
 
    hashed_token = _hash_token(request.token)
    user = db.query(User).filter(User.reset_token == hashed_token).first()
 
    if not user or not user.reset_token_expires:
        raise ValueError("Invalid or expired reset link")
 
    expires_at = user.reset_token_expires
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
 
    if expires_at < datetime.now(timezone.utc):
        raise ValueError("Invalid or expired reset link")
 
    user.hashed_password = hash_password(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()