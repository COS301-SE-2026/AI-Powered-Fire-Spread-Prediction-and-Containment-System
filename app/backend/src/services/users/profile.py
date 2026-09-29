from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.backend.src.models.users import User
from app.backend.src.schemas.user import UserUpdate

def update_profile(payload:UserUpdate, db: Session, current_user: User) -> User:
    if payload.email and payload.email != current_user.email:
        existing = db.query(User).filter(User.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=409, detail="Email already in use")
        current_user.email = payload.email

    if payload.name:
        current_user.name = payload.name
    
    if payload.surname:
        current_user.surname = payload.surname

    db.commit()
    db.refresh(current_user)
    return current_user