from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.schemas.auth import ForgotPasswordRequest, MsgResponse, ResetPasswordRequest
from app.backend.src.services.auth.email import send_password_reset_email  # adjust path if needed
from app.backend.src.services.auth.forgot_password import (
    GENERIC_MESSAGE,
    request_password_reset,
    reset_password,
)

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/forgot-password", response_model=MsgResponse)
def forgot_password_route(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    result = request_password_reset(db, request.email)

    if result:
        recipient, raw_token = result
        background_tasks.add_task(send_password_reset_email, recipient, raw_token)
 
    return {"message": GENERIC_MESSAGE}

@router.post("/reset-password", response_model=MsgResponse)
def reset_password_route(
    request: ResetPasswordRequest, db: Session = Depends(get_db)
):
    try:
        reset_password(db, request)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

    return {"message": "Your password has been reset. You can now log in."}
