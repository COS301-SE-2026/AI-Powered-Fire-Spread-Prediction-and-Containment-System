from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from db import get_db
from models import RoleRequestDB, User
from pydantic import BaseModel

router = APIRouter(prefix="/api/admin/roles", tags=["Admin"])

class RoleRequest(BaseModel):
    request_id: str
    user_id: str
    user_full_name: str | None = None
    email: str | None = None
    role: str
    status: str
    firefighter_license_id: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class RoleRequestList(BaseModel):
    data: List[RoleRequest]
    total: int

FIREFIGHTER_LICENSE_IDS = {"FF-1001", "FF-1002", "FF-2001", "FF-1003", "FF-1004", "FF-1005"}

@router.get("/role-requests", response_model=RoleRequestList)
def get_role_requests(db: Session = Depends(get_db)):
    requests = db.query(RoleRequestDB).all()
    return {"data": requests, "total": len(requests)}

@router.post("/role-requests/{request_id}/approve", response_model=RoleRequest)
def approve_role_request(request_id: str, db: Session = Depends(get_db)):
    req = db.query(RoleRequestDB).filter(RoleRequestDB.request_id == request_id).first()
    
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if req.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request already {req.status}")

    if req.role == "firefighter":
        if req.firefighter_license_id not in FIREFIGHTER_LICENSE_IDS:
            req.status = "rejected"
            db.commit()
            db.refresh(req)
            return req
        
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        
        raise HTTPException(status_code=404, detail="User not found")
    user.role = req.role
    req.status = "approved"

    db.commit()
    db.refresh(req)
    return req

@router.post("/role-requests/{request_id}/reject", response_model=RoleRequest)
def reject_role_request(request_id: str, db: Session = Depends(get_db)):
    req = db.query(RoleRequestDB).filter(RoleRequestDB.request_id == request_id).first()
    
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if req.status != "pending":
        raise HTTPException(status_code=400, detail="Request already processed")
    
    req.status = "rejected"
    db.commit()
    db.refresh(req)
    return req

@router.post("/role-requests/{request_id}/revoke", response_model=RoleRequest)
def revoke_role_request(request_id: str, db: Session = Depends(get_db)):
    req = db.query(RoleRequestDB).filter(RoleRequestDB.request_id == request_id).first()

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if req.status != "approved":
        raise HTTPException(status_code=400, detail="Only approved requests can be revoked")
    
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = "guest"
    req.status = "revoked"
    db.commit()
    db.refresh(req)
    return req
