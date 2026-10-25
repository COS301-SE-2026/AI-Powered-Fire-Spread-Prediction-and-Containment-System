from pydantic import BaseModel

class TwoFAStatusResponse(BaseModel):
    enabled: bool

class TwoFAEnableRequest (BaseModel):
    enabled: bool

class TwoFAToggleRequest(BaseModel):
    enabled: bool