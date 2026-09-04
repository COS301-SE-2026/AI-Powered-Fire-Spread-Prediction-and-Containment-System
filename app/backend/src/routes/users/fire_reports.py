from typing import Annotated, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.dependencies.auth import get_current_user_optional
from app.backend.src.models.users import User
from app.backend.src.schemas.fire_report import (
    FireReportCreate,
    FireReportDetailResponse,
    FireReportMapResponse,
)
from app.backend.src.services.users import fire_report
from app.backend.src.services.verification.verification_runner import run_verification

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/reported-fires", response_model=List[FireReportMapResponse])
def get_reported_fires(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)],
):
    return fire_report.get_fire_reports(db, current_user.id if current_user else None)


@router.post("/reported-fires", response_model=FireReportDetailResponse)
def create_fire_report(
    report: FireReportCreate,
    request: Request,
    background_tasks: BackgroundTasks,  # used to run auto verification
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_current_user_optional)],
):
    client_ip = (
        request.client.host
    )  # gets users IP used mainly for guests to be able to see in a way who reported it and to be used to protect against spam
    user_id = (
        current_user.id if current_user else None
    )  # Derives from a verified JWT for registered users

    created = fire_report.create_fire_report(report, db, client_ip, user_id)
    # let the autoverification of report run in the background
    background_tasks.add_task(run_verification, created["id"])
    return created
