from fastapi import Depends, HTTPException, Request
from jose import jwn, JWTError
from sqlalchemy.orm import Session
from db import get_db
from models.users import User
from auth import SECRET_KEY, ALGORITHM

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    