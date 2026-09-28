from sqlalchemy.orm import Session

from app.backend.src.enums.role_request_status import RequestStatus
from app.backend.src.models.role_request import RoleRequest
from app.backend.src.models.users import User
from app.backend.src.schemas.role_request import RoleRequestCreate

def create_role_request(db: Session, user: User, payload: RoleRequestCreate) -> RoleRequest:
    existing = (
        db.query(RoleRequest)
        .filter(RoleRequest.user_id == user.id, RoleRequest.status == RequestStatus.pending).first()
    )
    if existing:
        raise ValueError("You already have a pending role request")

        role_request = RoleRequest(
            user_id=user_id,
            requested_role=payload.requested_role,
            current_role=user_role,
            status=RequestStatus.pending,
        )
        db.add(role_request)
        db.commit()
        db.refresh(role_request)
        return role_request

def get_my_role_requests(db: Session, user: User):
    request = db.query(RoleRequest).filter(RoleRequest.user_id == user_id).all()
    return {"data": request, "total": len(request)}

def cancel_role_request(db: Session, user: User):
    role_request = db.query(RoleRequest).filter(RoleRequest.user_id == user.id, RoleRequest.status == RequestStatus.pending).first()

    if not role_request:
        return None

    db.delete(role_request)
    db.commit()
    return role_request