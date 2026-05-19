from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pyotp
from db import get_db_connection
from auth import verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])

class SetupRequest(BaseModel):
    email: str

class LoginRequest(BaseModel):
    username: str
    password: str

class SetupResponse(BaseModel):
    otpauth_url: str

class VerifyRequest(BaseModel):
    username: str
    code: str
@router.post("/login")
def login(payload: LoginRequest):
    # Replace in-memory lookup with database query
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, hashed_password, is_2fa_enabled, totp_secret FROM users WHERE email = %s",
                (payload.username,)
            )
            user = cur.fetchone()
            if not user:
                raise HTTPException(status_code=401, detail="Invalid credentials")

            # Verify password using your existing function
            if not verify_password(payload.password, user["hashed_password"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")

            if user["is_2fa_enabled"]:
                # 2FA required – but the real token will be issued by /verify-2fa
                # For compatibility with their original response:
                return {"message": "2FA required", "user_id": user["id"]}
            else:
                # No 2FA – issue JWT (you may want to call create_access_token here)
                # But keep original response for now:
                return {"status": "ok", "token": "dummy"}   # or integrate JWT
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

            # Store secret and enable 2FA
            cur.execute(
                "UPDATE users SET totp_secret = %s, is_2fa_enabled = TRUE WHERE email = %s",
                (secret, username)
            )
            conn.commit()

    return {"otpauth_url": otpauth_url}@router.post("/verify-2fa")
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
    return {"status": "verified"}