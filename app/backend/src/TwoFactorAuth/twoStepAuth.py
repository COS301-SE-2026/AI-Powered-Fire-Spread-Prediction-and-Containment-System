from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pyotp

router = APIRouter(prefix="/auth", tags=["Auth"])

# Mock in-memory store 
USERS = {
    "alice": {
        "password_hash": "$2b$12$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # bcrypt
        "totp_secret": None,
        "is_2fa_enabled": False,
    }
}

class LoginRequest(BaseModel):
    username: str
    password: str

class SetupResponse(BaseModel):
    otpauth_uri: str

class VerifyRequest(BaseModel):
    username: str
    code: str

@router.post("/login")
def login(payload: LoginRequest):
    user = USERS.get(payload.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # TODO: verify bcrypt password here
    # if not verify_password(payload.password, user["password_hash"]):
    #     raise HTTPException(status_code=401, detail="Invalid credentials")

    if user["is_2fa_enabled"]:
        return {"message": "2FA required"}
    return {"status": "ok"}

@router.post("/setup-2fa", response_model=SetupResponse)
def setup_2fa(username: str):
    user = USERS.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    secret = pyotp.random_base32()
    user["totp_secret"] = secret
    user["is_2fa_enabled"] = True

    # For Google Authenticator
    otpauth_url = pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name="FireSpreadApp")
    return {"otpauth_url": otpauth_url}

@router.post("/verify-2fa")
def verify_2fa(payload: VerifyRequest):
    user = USERS.get(payload.username)
    if not user or not user["is_2fa_enabled"]:
        raise HTTPException(status_code=404, detail="User not found or 2FA not enabled")
    
    totp = pyotp.TOTP(user["totp_secret"])
    if not totp.verify(payload.code, valid_window=1):
        raise HTTPException(status_code=401, detail="Invalid code")

    return {"status": "verified"}