from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.backend.src.enums.role_request_status import RequestStatus
from app.backend.src.enums.user_role import UserRole


class RoleRequestCreate(BaseModel):
    requested_role: UserRole

class RoleRequestReview(BaseModel):
    rejection_reason: Optional[str] = None

class UserSummary(BaseModel):
    id: str
    name: str
    surname: str
    email: str

    class Config:
        from_attributes = True

class ReviewerSummary(BaseModel):
    id: str
    name: str
    surname: str
    
    class Config:
        from_attributes = True


class RoleRequestResponse(BaseModel):
    request_id: str
    user: UserSummary
    requested_role: UserRole
    current_role: UserRole
    status: RequestStatus
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewer: Optional[ReviewerSummary] = None

    class Config:
        from_attributes = True


class RoleRequestList(BaseModel):
    data: List[RoleRequestResponse]
    total: int
