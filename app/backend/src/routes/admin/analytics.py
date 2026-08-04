from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db import get_db
from schemas.admin_analytics import AnalyticsOverviewResponse, KPIs
from services.admin.analytics_service import analytics_overview

router = APIRouter(prefix="/api/admin/analytics", tags=["Admin Analytics"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(db: Annotated[Session, Depends(get_db)]):
    return analytics_overview(db);