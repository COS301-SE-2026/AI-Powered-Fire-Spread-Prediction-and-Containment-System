from sqlalchemy.orm import Session

from app.backend.src.dependencies.auth import hash_password, verify_password
from app.backend.src.models.users import User
from app.backend.src.services.auth.forgot_password import MIN_PASSWORD_LENGTH

def edit_password(db: Session, user: User, current_password: str, new_password: str):
    if not verify_password(current_password, user.hashed_password):
        raise ValueError("Current password is incorrect")
    if len(new_password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
    if new_password == current_password:
        raise ValueError("New password must differ from the current one")

    user.hashed_password = hash_password(new_password)
    db.commit()