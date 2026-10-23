from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException 
from sqlalchemy.orm import Session

from app.backend.db import get_db 
from app.backend.src.dependencies.auth import get_current_user 
from app.backend.src.models.users import User
from app. backend.src.schemas.auth import MsgResponse, Two_FA_Create_Response 
from app.backend.src.schemas.two_factor_toggle import (
    TwoFADisableRequest,
    TwoFAEnableRequest,
    TwoFAStatusResponse,
)
from app.backend.src.services.auth.two_factor import setup_2fa
from app.backend.src.services.auth.two_factor_toggle import disable_2fa, enable_2fa

router = APIRouter(prefix="/api/auth/2fa", tags=["Auth"])

CurrentUser = Annotated[User, Depends (get_current_user)]
Db = Annotated[Session, Depends (get_db)]

@router.get("/status", response_model=TwoFAStatusResponse)
def two_fa_status_route (user: CurrentUser):
    return {"enabled": bool (user.is_2fa_enabled)}

@router.post("/setup", response_model=Two_FA_Create_Response)
def two_fa_setup_route(user: CurrentUser, db: Db):
    if user.is_2fa_enabled:
        raise HTTPException(status_code=400, detail="Two-factor authentication is already enabled")
    return setup_2fa(user.email, db)

@router.post("/enable", response_model=MsgResponse)
def two_fa_enable_route(request: TwoFAEnableRequest, user: CurrentUser, db: Db):
    try:
        enable_2fa (db, user, request.code)
    except ValueError as err:
        raise HТТРЕxception(status_code=400, detail=str(err))
    return {"message": "Two-factor authentication enabled"}

@router.post("/disable", response_model=MsgResponse)
def two_fa_disable_route(request: TwoFADisableRequest, user: CurrentUser, db: Db):
    try:
        disable_2fa(db, user, request.password, request. code)
    except ValueError as err:
        raise HТТРЕxception(status_code=400, detail=str(err))
    return {"message": "Two-factor authentication disabled"}