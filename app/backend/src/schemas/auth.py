from typing import Optional
from pydantic import BaseModel, EmailStr
from enums.user_role import UserRole

class RegisterRequest(BaseModel):
    email:EmailStr
    password:str
    name:str
    surname:str
    id_number:str
    license_number:Optional[str] = None

class LoginRequest(BaseModel):
    email:str
    password:str

class TokenResp(BaseModel):
    access_token:str
    token_type:str

class TwoFACreateResponse(BaseModel):
    otpauth_url:str

class TwoFAVerifyRequest(BaseModel):
    username:str
    code:str

class MsgResponse(BaseModel):
    message:str

class TwoFARequiredResponse(BaseModel):
    requires_2fa: bool = True
    email: str
    otpauth_url: Optional[str] = None #present at register for new secret but not for login because already set up

class LoginResponse(BaseModel):
    role: UserRole

LoginResponse.model_rebuild()
