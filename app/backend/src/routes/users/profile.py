from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.dependencies.auth import get_current_user
from app.backend.src.models.users import User
from app.backend.src.schemas.user import UserResponse

from app.backend.src.schemas.fire_report import FireReportDetailResponse
from app.backend.src.services.users import fire_report

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@router.get("/me/reported-fires/{report_ref}", response_model=FireReportDetailResponse)
def get_my_reported_fires(
    report_ref: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        report = fire_report.get_fire_report_by_id(report_ref, db)
    except ValueError:
        raise HTTPException(status_code=404, detail="Report not found")
    if report["user_id"] != current_user.id:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

