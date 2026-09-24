# scheme for volunteer GPU workers
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class WorkerEnrollmentKeyRequest(BaseModel):
    label: str = Field("Home desktop", min_length=1, max_length=100)
    gpu_name: str = Field("Unknown GPU", max_length=150)

class WorkerEnrollmentKeyResponse(BaseModel):
    registration_key: str
    expires_in_seconds: int
    docker_command: str


class WorkerRegisterRequest(BaseModel):
    registration_key: str = Field(..., min_length=10)
    label:str = Field("volunteer-desktop", min_length=2, max_length=100)
    gpu_name: str = Field(..., max_length=100)
    vram_mb: int = Field(..., ge=1024)
    driver_version: Optional[str] = None
    cuda_capable: bool = True


class WorkerTokenResponse(BaseModel):
    access_token: str
    token_type: str= "bearer"
    worker_id: str


class GPUWorkerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    label: str
    gpu_name: str
    vram_mb: int
    status: str
    last_heartbeat: Optional[datetime] = None
    activated_at: datetime
    deactivated_at: Optional[datetime] = None
    removed_at: Optional[datetime] = None
    removal_reason: Optional[str] = None


class WorkerNodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    label: str
    gpu_name: str
    vram_mb: int
    status: str
    last_heartbeat: Optional[datetime] = None
    activated_at: datetime
    deactivated_at: Optional[datetime] = None
    removed_at: Optional[datetime] = None
    removal_reason: Optional[str] = None


class WorkerStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    label: str
    gpu_name: str
    vram_mb: int
    status: str
    consecutive_failures: int
    last_heartbeat: Optional[datetime] = None
    activated_at: datetime
    deactivated_at: Optional[datetime] = None
    removed_at: Optional[datetime] = None
    removal_reason: Optional[str] = None


class WorkerRemovalRequest(BaseModel):
    reason: Optional[str] = Field(None, max_length=500)


class ComputeDistrubutionRatio(BaseModel):
    active: int
    busy: int
    quarantined: int
    offline: int
    total: int