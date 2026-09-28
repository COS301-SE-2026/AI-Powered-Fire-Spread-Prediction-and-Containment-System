from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.schemas.role_request import RoleRequestCreate, RoleRequestList, RoleRequestResponse
from app.backend.src.services.users import role_request

from app.backend.src.dependencies.auth import get_current_user
from app.backend.src.models.users import User

router = APIRouter(
    prefix="/api/users", tags=["Users"], dependencies=[Depends(get_current_user)]
)

@router.get("/role-requests/me", response_model=RoleRequestList)
def get_my_role_requests(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return role_request.get_my_role_requests(db, user)


@router.post("/role-requests", response_model=RoleRequestResponse, status_code=201)
def apply_for_role(payload: RoleRequestCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try: 
        return role_request.create_role_request(db, user, payload)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error))

@router.delete("/role-requests/me", response_model=RoleRequestResponse)
def cancel_my_role_request(db: Session = Depends(get_db), user: User = Depends(get_current_user) ):
    request = role_request.cancel_role_request(db, user)

    if not request:
        raise HTTPException(status_code=404, detail="No pending role request to cancel")
    return request