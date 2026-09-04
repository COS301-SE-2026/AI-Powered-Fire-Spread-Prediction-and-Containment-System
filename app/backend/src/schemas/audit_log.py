from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.backend.src.enums.audit_action import AuditAction


class AuditLogResponse(BaseModel):
    id: str
    timestamp: datetime
    user_email: Optional[str] = None
    action: AuditAction
    detail: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    data: list[AuditLogResponse]
    total: int
    page: int
    limit: int
    pages: int
