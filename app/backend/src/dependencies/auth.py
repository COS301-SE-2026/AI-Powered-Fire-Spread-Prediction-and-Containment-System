import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.enums.user_role import UserRole
from app.backend.src.models.users import User

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


def hash_password(password: str) -> str:
    """Return bcrypt hash of the password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token."""
    if not SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY environment variable not set")
    to_encode = data.copy()

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    """
    Returns user_id claim if token is valid, else None.
    Used by notifications WebSocket handshake where there is no cookie and no Request object
    to pull a header from.
    """
    if not SECRET_KEY:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id")
    except JWTError:
        return None


def extract_token(request: Request) -> Optional[str]:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer"):
            token = auth_header.split(" ", 1)[1]
    return token


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = extract_token(request)

    if not token:
        raise HTTPException(status_code=401, detail="Not Authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid/Expired Token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def require_role(*allowed_roles):
    """Usage on any route that needs restricting:
    @router.get("/dashboard/summary)
    def get_summary(user: User = Depends(require_role(UserRole.admin))): ...
    """

    def role_checker(user: User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource",
            )
        return user

    return role_checker


def get_current_user_optional(
    request: Request, db: Session = Depends(get_db)
) -> Optional[User]:
    """Same as get_current_user but returns None instead of raising when no/invalid token for routes that allow guests"""
    token = extract_token(request)
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
    except JWTError:
        return None

    if not user_id:
        return None

    return db.query(User).filter(User.id == user_id).first()


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """Dependency ensures the current user has an Admin privilage"""
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admin privileges needed",
        )
    return current_user
