import pyotp
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import get_db_connection
from auth import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

class SetupResponse(BaseModel):
    otpauth_url: str

class VerifyRequest(BaseModel):
    username: str
    code: str

@router.post("/setup-2fa", response_model=SetupResponse)
def setup_2fa(username: str):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email = %s", (username,))
            user = cur.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            secret = pyotp.random_base32()
            otpauth_url = pyotp.TOTP(secret).provisioning_uri(name=username, issuer_name="FireSpreadApp")

            cur.execute(
                "UPDATE users SET totp_secret = %s, is_2fa_enabled = TRUE WHERE email = %s",
                (secret, username)
            )
            conn.commit()

    return {"otpauth_url": otpauth_url}

@router.post("/verify-2fa")
def verify_2fa(payload: VerifyRequest):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, totp_secret FROM users WHERE email = %s AND is_2fa_enabled = TRUE",
                (payload.username,)
            )
            user = cur.fetchone()
            if not user or not user["totp_secret"]:
                raise HTTPException(status_code=404, detail="User not found or 2FA not enabled")

            totp = pyotp.TOTP(user["totp_secret"])
            if not totp.verify(payload.code, valid_window=1):
                raise HTTPException(status_code=401, detail="Invalid code")

            # Issue JWT after successful 2FA
            access_token = create_access_token(data={"sub": user["email"], "user_id": user["id"]})
            return {"access_token": access_token, "token_type": "bearer"}