from typing import Annotated, Union

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.backend.src.dependencies.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
)
from app.backend.db import get_db
from app.backend.src.schemas.auth import (
    LoginRequest,
    LoginResponse,
    MeResponse,
    Two_FA_Required_Response,
)
from app.backend.src.services.auth.login import login_user
from app.backend.src.models.users import User

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=Union[LoginResponse, Two_FA_Required_Response])
def login_route(
    request: LoginRequest, response: Response, db: Annotated[Session, Depends(get_db)]
):
    try:
        result = login_user(db, request)
    except HTTPException:
        raise
    except ValueError as err:
        raise HTTPException(status_code=401, detail=str(err))

    if result.get("requires_2fa"):
        return result

    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=False,  # MUST CHANGE TO TRUE WHEN SERVING OVER HTTPS
        samesite="lax",
        max_age=60 * ACCESS_TOKEN_EXPIRE_MINUTES,
        path="/",
    )

    return {
        "access_token": result["access_token"],
        "role": result["role"],
    }


@router.get("/me", response_model=MeResponse)
def me_route(user: User = Depends(get_current_user)):
    return {"role": user.role}
