from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.backend.src.dependencies.auth import ACCESS_TOKEN_EXPIRE_MINUTES
from app.backend.db import get_db
from app.backend.src.schemas.auth import (
    LoginResponse,
    Two_FA_Create_Response,
    Two_FA_Verify_Request,
)
from app.backend.src.services.auth.two_factor import setup_2fa, verify_2fa

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/setup-2fa", response_model=Two_FA_Create_Response)
def setup_2fa_route(username: str, db: Session = Depends(get_db)):
    try:
        return setup_2fa(username, db)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))


@router.post("/verify-2fa", response_model=LoginResponse)
def verify_2fa_route(
    request: Two_FA_Verify_Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
):
    try:
        result = verify_2fa(db, request)
    except ValueError as err:
        raise HTTPException(status_code=401, detail=str(err))

    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=False,  # CHANGE TO TRUE WHEN ON HTTPS
        samesite="lax",
        max_age=60 * ACCESS_TOKEN_EXPIRE_MINUTES,
        path="/",
    )

    return {"role": result["role"]}
