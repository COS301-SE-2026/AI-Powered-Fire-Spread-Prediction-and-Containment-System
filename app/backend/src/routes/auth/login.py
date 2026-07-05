from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from schemas.auth import LoginRequest, TokenResp, Two_FA_Required_Response
from services.auth.login import login_user
from typing import Union

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/login", response_model=Union[TokenResp, Two_FA_Required_Response])
def login_route(request: LoginRequest, db:Session = Depends(get_db)):
    try:
        return login_user(db, request)
    except ValueError as err:
        raise HTTPException(status_code=401, detail=str(err))