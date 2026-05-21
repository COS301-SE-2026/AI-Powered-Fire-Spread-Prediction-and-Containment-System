from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal

router = APIRouter(prefix="/api/admin/roles", tags=["Admin"])

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
    user_full_name: str | None = None
    email: str | None = None
    role: RoleType
    status: StatusType
    firefighter_license_id: str | None = None
    created_at: str | None = None


# MOCK DATA 
ROLE_REQUESTS = [
    {
        "request_id": "req_1",
        "user_id": "user_1",
        "user_full_name": "James Smith",
        "email": "j.smith@email.com",
        "role": "firefighter",
        "status": "pending",
        "firefighter_license_id": "FF-1001",
        "created_at": "2026-05-20T09:12:00Z",
    },
    {
        "request_id": "req_2",
        "user_id": "user_2",
        "user_full_name": "Anna Dlamini",
        "email": "a.dlamini@email.com",
        "role": "admin",
        "status": "pending",
        "created_at": "2026-05-19T14:30:00Z",
    },
    {
        "request_id": "req_3",
        "user_id": "user_3",
        "user_full_name": "Peter Nkosi",
        "email": "p.nkosi@email.com",
        "role": "firefighter",
        "status": "approved",
        "firefighter_license_id": "FF-1002",
        "created_at": "2026-05-18T11:00:00Z",
    },
    {
        "request_id": "req_4",
        "user_id": "user_4",
        "user_full_name": "Lerato Botha",
        "email": "l.botha@email.com",
        "role": "admin",
        "status": "rejected",
        "created_at": "2026-05-17T08:45:00Z",
    },
    {
        "request_id": "req_5",
        "user_id": "user_5",
        "user_full_name": "Thabo Mokoena",
        "email": "t.mokoena@email.com",
        "role": "firefighter",
        "status": "rejected",
        "firefighter_license_id": "FF-2001",
        "created_at": "2026-05-16T10:20:00Z",
    },
    {
        "request_id": "req_6",
        "user_id": "user_6",
        "user_full_name": "Sipho Ndlovu",
        "email": "s.ndlovu@email.com",
        "role": "firefighter",
        "status": "pending",
        "firefighter_license_id": "FF-3001",
        "created_at": "2026-05-15T07:30:00Z",
    },
    {
        "request_id": "req_7",
        "user_id": "user_7",
        "user_full_name": "Priya Naidoo",
        "email": "p.naidoo@email.com",
        "role": "admin",
        "status": "approved",
        "created_at": "2026-05-14T13:00:00Z",
    },
    {
        "request_id": "req_8",
        "user_id": "user_8",
        "user_full_name": "Willem Joubert",
        "email": "w.joubert@email.com",
        "role": "firefighter",
        "status": "rejected",
        "firefighter_license_id": "FF-3002",
        "created_at": "2026-05-13T09:45:00Z",
    },
    {
        "request_id": "req_9",
        "user_id": "user_9",
        "user_full_name": "Nomsa Khumalo",
        "email": "n.khumalo@email.com",
        "role": "firefighter",
        "status": "pending",
        "firefighter_license_id": "FF-3003",
        "created_at": "2026-05-12T11:20:00Z",
    },
    {
        "request_id": "req_10",
        "user_id": "user_10",
        "user_full_name": "Brendan Fourie",
        "email": "b.fourie@email.com",
        "role": "admin",
        "status": "pending",
        "created_at": "2026-05-11T08:00:00Z",
    },
    {
        "request_id": "req_11",
        "user_id": "user_11",
        "user_full_name": "Zanele Mokoena",
        "email": "z.mokoena@email.com",
        "role": "firefighter",
        "status": "approved",
        "firefighter_license_id": "FF-4001",
        "created_at": "2026-05-10T14:30:00Z",
    },
    {
        "request_id": "req_12",
        "user_id": "user_12",
        "user_full_name": "Ruan van der Berg",
        "email": "r.vdberg@email.com",
        "role": "admin",
        "status": "rejected",
        "created_at": "2026-05-09T10:15:00Z",
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