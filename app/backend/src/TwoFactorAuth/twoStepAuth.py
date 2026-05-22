import pyotp
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_db
from models import User
from auth import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


class SetupResponse(BaseModel):
    otpauth_url: str


class VerifyRequest(BaseModel):
    username: str
    code: str


@router.post("/setup-2fa", response_model=SetupResponse)
def setup_2fa(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    secret = pyotp.random_base32()
    otpauth_url = pyotp.TOTP(secret).provisioning_uri(
        name=username, issuer_name="FireSpreadApp"
    )

    user.totp_secret = secret
    user.is_2fa_enabled = True
    db.commit()

    return {"otpauth_url": otpauth_url}


@router.post("/verify-2fa")
def verify_2fa(payload: VerifyRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.email == payload.username, User.is_2fa_enabled == True)
        .first()
    )
    if not user or not user.totp_secret:
        raise HTTPException(status_code=404, detail="User not found or 2FA not enabled")

    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(payload.code, valid_window=1):
        raise HTTPException(status_code=401, detail="Invalid code")

    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}