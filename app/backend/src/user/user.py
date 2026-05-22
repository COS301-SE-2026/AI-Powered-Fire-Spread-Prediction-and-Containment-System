from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from db import get_db
from models import User

router = APIRouter(prefix="/api/users", tags=["Users"])

class UserOut(BaseModel):
    id: str
    email: str
    name: str
    surname: str
    role: str
    created_at: datetime
    class Config:
        from_attributes = True

@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user