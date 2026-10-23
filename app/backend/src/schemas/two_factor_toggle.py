from pydantic import BaseModel

class TwoFAStatusResponse(BaseModel):
    enabled: bool

class TwoFAEnableRequest (BaseModel):
    code: str

class TwoFADisableRequest(BaseModel):
    password: str
    code: str