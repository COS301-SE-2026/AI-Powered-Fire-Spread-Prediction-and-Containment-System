from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.dependencies.auth import get_current_user
from app.backend.src.models.users import User
from app.backend.src.schemas.auth import MsgResponse
from app.backend.src.schemas.edit_password import ChangePasswordRequest
from app.backend.src.services.auth.edit_password import edit_password

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/edit_password", response_model=MsgResponse)
def edit_password_route(request: ChangePasswordRequest, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    try:
        edit_password(db, user, request.current_password, request.new_password)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return {"message": "Password updated"}
