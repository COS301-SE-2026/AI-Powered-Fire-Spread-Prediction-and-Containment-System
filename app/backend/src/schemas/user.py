from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from enums.user_role import UserRole


class UserCreate(BaseModel):
    name: str
    surname: str
    email: str
    id_number: str
    license_number: Optional[str] = None
    role: UserRole = UserRole.user


class UserResponse(BaseModel):
    id: str
    name: str
    surname: str
    email: str
    role: UserRole
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
