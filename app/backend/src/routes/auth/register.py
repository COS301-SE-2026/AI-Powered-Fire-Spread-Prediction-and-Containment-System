from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.schemas.auth import RegisterRequest, Two_FA_Required_Response
from app.backend.src.services.auth.register import register_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=Two_FA_Required_Response, status_code=201)
def register_route(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        pending = register_user(db, request)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))


    return {
        "requires_2fa": True,
        "email": pending["email"],
        "otpauth_url": pending["otpauth_url"],
        "registration_token": pending["registration_token"]
    }
