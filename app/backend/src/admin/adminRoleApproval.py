from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal

router = APIRouter(prefix="/api/admin/roles", tags=["Admin"])

# Firefighters auto approved if they have a valid license, otherwise rejected. Admins require manual approval.

RoleType = Literal["firefighter", "admin"]
StatusType = Literal["pending", "approved", "rejected"]

# MOCK FIREFIGHTER LICENSES
FIREFIGHTER_LICENSE_IDS = {
    "FF-1001",
    "FF-1002",
    "FF-2001",
}

class RoleRequest(BaseModel):
    request_id: str
    user_id: str
    role: RoleType
    status: StatusType
    firefighter_license_id: str | None = None   #only required for firefighters


# MOCK DATA 
ROLE_REQUESTS = [
    {
        "request_id": "req_1",
        "user_id": "user_1",
        "role": "firefighter",
        "status": "pending",
        "firefighter_license_id": "FF-1001",
    },
    {
        "request_id": "req_2",
        "user_id": "user_2",
        "role": "admin",
        "status": "pending",
    },
]

@router.get("/role-requests", response_model=List[RoleRequest])
def get_role_requests():
    return ROLE_REQUESTS

@router.post("/role-requests/{request_id}/approve", response_model=RoleRequest)
def approve_role_request(request_id: str):
    for req in ROLE_REQUESTS:
        if request_id == req["request_id"]:
            if req["status"] != "pending":
                raise HTTPException(status_code=400, detail="Request already processed")
            
            if req["role"] == "firefighter":
                license_id = req.get("firefighter_license_id")
                if not license_id or license_id not in FIREFIGHTER_LICENSE_IDS:
                    req["status"] = "rejected"
                    return req  # Automatically reject if license is invalid or missing

            req["status"] = "approved"
            return req
    raise HTTPException(status_code=404, detail="Request not found")

@router.post("/role-requests/{request_id}/reject", response_model=RoleRequest)
def reject_role_request(request_id: str):
    for req in ROLE_REQUESTS:
        if request_id == req["request_id"]:
            if req["status"] != "pending":
                raise HTTPException(status_code=400, detail="Request already processed")
            req["status"] = "rejected"
            return req
    raise HTTPException(status_code=404, detail="Request not found")