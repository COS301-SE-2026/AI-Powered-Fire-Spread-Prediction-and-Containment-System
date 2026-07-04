from enums.user_role import UserRole
from enums.role_request_status import RequestStatus
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class RoleRequestCreate(BaseModel):
    current_role:UserRole

class UserSummary(BaseModel):
    id:str
    name:str
    surname:str
    email:str
    license_number:Optional[str] = None

    class Config:
        from_attributes = True
    
class RoleRequestResponse(BaseModel):
    request_id:str
    user:UserSummary
    requested_role:UserRole
    current_role:UserRole
    status:RequestStatus
    firefighter_license_id: Optional[str] = None
    created_at:datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None

    class Config:
        from_attributes = True

class RoleRequestList(BaseModel):
    data:List[RoleRequestResponse]
    total:int