from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.dependencies.auth import get_current_user
from app.backend.src.models.users import User
from app.backend.src.schemas.user import UserResponse

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
