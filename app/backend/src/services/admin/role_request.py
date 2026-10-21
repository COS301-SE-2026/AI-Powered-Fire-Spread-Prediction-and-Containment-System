import uuid
from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.backend.src.enums.role_request_status import RequestStatus
from app.backend.src.models.role_request import RoleRequest
from app.backend.src.models.users import User
from app.backend.src.schemas.role_request import RoleRequestList, RoleRequestResponse
from app.backend.src.services.verification.reporter_trust import (
    reporter_report_counts,
    trust_score_from_counts,
)

def get_role_requests(db: Session):
    request = db.query(RoleRequest).all()
    return role_request_list(db, request)


def approve_role_request(request_id: str, admin_id: str, db: Session):
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


def reject_role_request(request_id: str, admin_id: str, db: Session):
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


def revoke_role_request(request_id: str, admin_id: str, db: Session):
    request = db.query(RoleRequest).filter(RoleRequest.request_id == request_id).first()

    if not request:
        return None

    if request.status != RequestStatus.approved:
        raise ValueError("Only approved reqeusts may be revoked!!")

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

def search_report_table(db: Session, key: str):
    pattern = f"%{key.strip()}%"
    request = (
        db.query(RoleRequest)
        .outerjoin(User, RoleRequest.user_id == User.id)
        .filter(
            or_(
                User.name.ilike(f"%{key}%"),
                User.surname.ilike(f"%{key}%"),
            )
        )
        .all()
    )
    return role_request_list(db, request)

def role_request_list(db: Session, requests: list[RoleRequest]) -> RoleRequestList:
    """List with each reporters trust data"""
    counts = reporter_report_counts([req.user_id for req in requests], db)

    items: list[RoleRequestResponse] = []
    for req in requests:
        verified, rejected = counts[req.user_id]
        item = RoleRequestResponse.model_validate(req)
        item.reports_verified = verified 
        item.reports_rejected = rejected
        item.trust_score = trust_score_from_counts(verified, rejected)
        items.append(item)
    return RoleRequestList(data=items, total=len(items))

