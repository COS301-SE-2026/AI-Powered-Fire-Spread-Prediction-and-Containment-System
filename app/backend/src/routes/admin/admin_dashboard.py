from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from db import get_db
from schemas.admin_dashboard import DashboardSummaryResponse
from services.admin.dashboard_service import dashboard_summary

from dependencies.auth import get_current_admin_user

router = APIRouter(
    prefix="/api/admin/dashboard",
    tags=["Admin Dashboard"],
    # comment when need admin auth
    dependencies=[Depends(get_current_admin_user)],
)


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    responses={400: {"description": "Could not retrieve dashboard summary"}},
)
def get_dashboard_summary(db: Session = Depends(get_db)) -> Any:
    try:
        return dashboard_summary(db)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Could not retrieve dashboard summary"
        )
