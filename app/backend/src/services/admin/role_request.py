from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timezone
from src.models.role_request import RoleRequest
from src.models.users import User
from src.enums.role_request_status import RequestStatus

def get_role_requests(db:Session):
    request = db.query(RoleRequest).all()
    return {"data": request, "total":len(request)}

def approve_role_request(request_id:str, admin_id: str, db:Session):
    request = db.query(RoleRequest).filter(RoleRequest.request_id == request_id).first()
    
    if not request:
        return None
    
    if request.status != RequestStatus.pending:
        raise ValueError(f"Role is already {request.status.value}")
    
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise ValueError("User not found!!")
    
    user.role = request.requested_role
    request.status = RequestStatus.approved
    request.reviewed_by = admin_id
    request.reviewed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(request)
    return request


def reject_role_request(request_id:str, admin_id: str, db:Session):
    request = db.query(RoleRequest).filter(RoleRequest.request_id == request_id).first()
    
    if not request:
        return None
    
    if request.status != RequestStatus.pending:
        raise ValueError(f"Role is already {request.status.value}")
    
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise ValueError("User not found!!")
    
    request.status = RequestStatus.rejected
    request.reviewed_by = admin_id
    request.reviewed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(request)
    return request

def revoke_role_request(request_id:str, admin_id: str, db:Session):
    request = db.query(RoleRequest).filter(RoleRequest.request_id == request_id).first()
    
    if not request:
        return None
    
    if request.status != RequestStatus.approved:
        return None
    
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise ValueError("User not found!!")
    
    user.role = request.current_role
    request.status = RequestStatus.revoked
    request.reviewed_by = admin_id
    request.reviewed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(request)
    return request
