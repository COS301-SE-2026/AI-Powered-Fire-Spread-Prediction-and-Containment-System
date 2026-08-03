# This is for any route that needs to check if person is logged and has correct role
# Reads cookie, decodes token and either blocks or allows request
from typing import Optional

from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from auth import ALGORITHM, SECRET_KEY
from app.backend.db import get_db
from enums.user_role import UserRole
from models.users import User


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

    def role_checker(user: User = Depends(require_role(UserRole.admin))):
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


def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    """Dependency ensures the current user has an Admin privilage"""
    if current_user.get("role") != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admin privileges needed",
        )
    return current_user
