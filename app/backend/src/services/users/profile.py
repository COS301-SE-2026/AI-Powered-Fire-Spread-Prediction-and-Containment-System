from fastapi import HTTPException
from sqlalchemy import func 
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.backend.src.models.users import User
from app.backend.src.schemas.user import UserUpdate

def update_profile(payload:UserUpdate, db: Session, current_user: User) -> User:
    email = (payload.email or "").strip().lower()
    name = (payload.name or "").strip()
    surname = (payload.surname or "").strip()
    
    if email and email != current_user.email.lower():
        existing = db.query(User).filter(func.lower(User.email) == email).first()
        if existing:
            raise HTTPException(status_code=409, detail="Email already in use")
        current_user.email = email

    if name:
        current_user.name = name
    
    if surname:
        current_user.surname = surname

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already in use") from exc
    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(current_user)
    return current_user