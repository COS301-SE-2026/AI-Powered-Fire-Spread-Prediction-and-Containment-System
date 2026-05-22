from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from db import get_db
from models import User
from auth import verify_password, create_access_token

router = APIRouter(prefix="/api", tags=["Auth"])


class UserLogin(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token or 2FA required message."""
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if db_user.is_2fa_enabled:
        return {
            "message": "2FA required",
            "user_id": db_user.id,
            "email": db_user.email,
        }

    access_token = create_access_token(
        data={"sub": db_user.email, "user_id": db_user.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}