import uuid
import secrets

from sqlalchemy.orm import Session

from app.backend.src.dependencies.auth import hash_password
from app.backend.src.services.auth.pending_registration import create_pending_registration
from app.backend.src.services.verification.register_verification import validate_sa_id
from app.backend.src.models.users import User
from app.backend.src.schemas.auth import RegisterRequest


def register_user(db: Session, request: RegisterRequest):
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise ValueError("Email already exists please enter a valid email.")
    
    return create_pending_registration(request, hash_password(request.password))
