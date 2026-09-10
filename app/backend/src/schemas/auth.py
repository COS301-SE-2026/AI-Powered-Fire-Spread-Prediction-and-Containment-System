from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.backend.src.enums.user_role import UserRole
from app.backend.src.services.verification.register_verification import validate_sa_id


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    surname: str
    id_number: str
    requested_role: UserRole = UserRole.user

    @field_validator("id_number")
    @classmethod
    def check_id_number(cls, v: str) -> str:
        return validate_sa_id(v)["id_number"]


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResp(BaseModel):
    access_token: str
    token_type: str


class Two_FA_Create_Response(BaseModel):
    otpauth_url: str


class Two_FA_Verify_Request(BaseModel):
    username: str
    code: str


class MsgResponse(BaseModel):
    message: str


class Two_FA_Required_Response(BaseModel):
    requires_2fa: bool = True
    email: str
    otpauth_url: Optional[str] = None  # present at register for new secret but not for login because already set up
    registration_token: Optional[str] = None
    pending_approval: bool = False


class CompleteRegistrationRequest(BaseModel):
    registration_token: str
    code: str

class LoginResponse(BaseModel):
    role: UserRole
    access_token: str 


class MeResponse(BaseModel):
    role: UserRole

class TwoFAVerifyResponse(BaseModel):
    role: str


LoginResponse.model_rebuild()
