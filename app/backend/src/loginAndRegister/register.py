import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from db import get_db
from models import User
from auth import hash_password

router = APIRouter(prefix="/api", tags=["Auth"])


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    surname: str
    id_number: str
    licence_number: Optional[str] = None
    role: str = "User"


class MessageResponse(BaseModel):
    message: str


@router.post("/api/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        id=f"usr_{uuid.uuid4().hex[:8]}",
        email=user.email,
        hashed_password=hash_password(user.password),
        name=user.name,
        surname=user.surname,
        id_number=user.id_number,
        license_number=user.licence_number,
        role=user.role,
        is_2fa_enabled=False,
    )
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}