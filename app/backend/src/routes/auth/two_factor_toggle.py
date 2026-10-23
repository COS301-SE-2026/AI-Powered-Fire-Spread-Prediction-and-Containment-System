from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException 
from sqlalchemy.orm import Session

from app.backend.db import get_db 
from app.backend.src.dependencies.auth import get_current_user 
from app.backend.src.models.users import User
from app. backend.src.schemas.auth import MsgResponse
from app.backend.src.schemas.two_factor_toggle import (
    TwoFAStatusResponse,
    TwoFAToggleRequest
)
from app.backend.src.services.auth.two_factor_toggle import set_2fa_enabled

router = APIRouter(prefix="/api/auth/2fa", tags=["Auth"])

CurrentUser = Annotated[User, Depends (get_current_user)]
Db = Annotated[Session, Depends (get_db)]

@router.get("/status", response_model=TwoFAStatusResponse)
def two_fa_status_route (user: CurrentUser):
    return {"enabled": bool (user.is_2fa_enabled)}

@router.post("/toggle", response_model=MsgResponse)
def two_fa_toggle_route(request: TwoFAToggleRequest, user: CurrentUser, db: Db):
    try:
        set_2fa_enabled(db, user, request.enabled)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return {"message": "Two-factor authentication updated"}