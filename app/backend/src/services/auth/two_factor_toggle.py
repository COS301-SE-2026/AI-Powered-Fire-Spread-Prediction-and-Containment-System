import pyotp
from sqlalchemy.orm import Session

from app.backend.src.dependencies.auth import verify_password 
from app.backend.src.models.users import User

def _code_is_valid (secret: str | None, code: str) -> bool:
    if not secret:
        return False
    return pyotp.TOTP(secret).verify(code, valid_window=1)

def enable_2fa(db: Session, user: User, code: str) -> None:
    if user.is_2fa_enabled:
        raise ValueError("Two-factor authentication is already enabled")
    if not _code_is_valid(user. totp_secret, code) :
        raise ValueError ("Invalid authenticator code")
    user.is_2fa_enabled = True
    db.commit()

def disable_2fa(db: Session, user: User, password: str, code: str) -> None:
    if not user.is_2fa_enabled:
        raise ValueError("Two-factor authentication is not enabled")
    if not verify_password(password, user.hashed_password):
        raise ValueError ("Password is incorrect") 
    if not _code_is_valid(user. totp_secret, code):
        raise ValueError ("Invalid authenticator code")
    user. is_2fa_enabled = False
    user. totp_secret = None
    db.commit ()