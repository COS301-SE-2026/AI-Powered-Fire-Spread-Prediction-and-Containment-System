# scheme for volunteer GPU workers
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class WorkerRequestCreate(BaseModel):
    label: str = Field(..., min_length=2, max_length=100)
    gpu_name: str = Field(..., min_length=2, max_length=100)
    vram_mb: int = Field(..., ge=1024)

class WorkerRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    label: str
    gpu_name: str
    vram_mb: int
    status: str
    created_at: datetime
    updated_at: datetime

class WorkerRegisterRequest(BaseModel):
    registration_key: str = Field(..., min_length=10)
    gpu_name: str
    vram_mb: int
    driver_version: Optional[str] = None

class WorkerTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    worker_id: str

class WorkerApprovalResponse(BaseModel):
    request_id: str
    status: str
    registration_key: str
    expires_in_seconds: int