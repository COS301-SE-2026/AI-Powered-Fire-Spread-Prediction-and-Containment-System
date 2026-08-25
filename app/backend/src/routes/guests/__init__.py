from fastapi import APIRouter

from .fire_reports import router as fire_report_router
from .guests_dashboard import router as dashboard_router
from .nearby_fires import router as guest_nearby_fires_router

router = APIRouter()
router.include_router(fire_report_router)
router.include_router(dashboard_router)
router.include_router(guest_nearby_fires_router)