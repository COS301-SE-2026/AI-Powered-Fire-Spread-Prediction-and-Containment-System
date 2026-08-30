from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from schemas.role_request import RoleRequestList, RoleRequestResponse
from services.admin import role_request

from dependencies.auth import get_current_admin_user
from models.users import User

router = APIRouter(
    prefix="/api/admin", tags=["Admin"], dependencies=[Depends(get_current_admin_user)]
)


@router.get("/role-requests", response_model=RoleRequestList)
def get_role_requests(db: Session = Depends(get_db)):
    return role_request.get_role_requests(db)


@router.put("/role-requests/{request_id}/approve", response_model=RoleRequestResponse)
def approve_role_request(
    request_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    admin_id = admin.id
    try:
        request = role_request.approve_role_request(request_id, admin_id, db)

        if not request:
            raise HTTPException(status_code=404, detail="Role request is not found")

        return request
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/role-requests/{request_id}/reject", response_model=RoleRequestResponse)
def reject_role_request(
    request_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    admin_id = admin.id
    try:
        request = role_request.reject_role_request(request_id, admin_id, db)

        if not request:
            raise HTTPException(status_code=404, detail="Role request is not found")

        return request
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/role-requests/{request_id}/revoke", response_model=RoleRequestResponse)
def revoke_role_request(
    request_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    admin_id = admin.id
    try:
        request = role_request.revoke_role_request(request_id, admin_id, db)

        if not request:
            raise HTTPException(status_code=404, detail="Role request is not found")

        return request
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
