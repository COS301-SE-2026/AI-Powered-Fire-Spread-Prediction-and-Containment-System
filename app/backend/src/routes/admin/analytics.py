from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.backend.src.schemas.admin_analytics import AnalyticsOverviewResponse, KPIs
from app.backend.src.services.admin.analytics_service import analytics_overview
from app.backend.src.dependencies.auth import get_current_admin_user

router = APIRouter(
    prefix="/api/admin/analytics",
    tags=["Admin Analytics"],
    dependencies=[Depends(get_current_admin_user)],
)


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    responses={404: {"description": "Could not retrieve analytics overview"}},
)
def get_analytics_overview(db: Annotated[Session, Depends(get_db)]):
    try:
        return analytics_overview(db)
    except ValueError:
        raise HTTPException(
            status_code=404, detail="Could not retrieve analytics overview"
        )
