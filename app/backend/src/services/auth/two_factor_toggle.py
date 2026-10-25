from sqlalchemy.orm import Session

from app.backend.src.models.users import User

def set_2fa_enabled(db: Session, user: User, enabled: bool) -> None:
    if enabled and not user.totp_secret:
        raise ValueError("Two-factor authentication was never set up for this account")
    user.is_2fa_enabled = enabled
    db.commit()

