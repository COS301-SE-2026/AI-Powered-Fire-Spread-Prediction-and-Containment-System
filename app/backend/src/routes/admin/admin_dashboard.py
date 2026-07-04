from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from src.schemas.admin_dashboard import DashboardSummaryResponse
from src.db import get_db