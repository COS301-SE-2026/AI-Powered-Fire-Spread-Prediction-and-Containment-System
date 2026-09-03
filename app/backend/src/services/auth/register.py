import uuid

from sqlalchemy.orm import Session

from dependencies.auth import hash_password
from models.users import User
from schemas.auth import RegisterRequest


def register_user(db: Session, request: RegisterRequest):
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise ValueError("Email already exists please enter a valid email.")

    new_user = User(
        id=f"usr_{uuid.uuid4().hex[:8]}",
        email=request.email,
        hashed_password=hash_password(request.password),
        name=request.name,
        surname=request.surname,
        id_number=request.id_number,
        license_number=request.license_number,
        is_2fa_enabled=False,
    )

    db.add(new_user)
    db.commit()
    return new_user
