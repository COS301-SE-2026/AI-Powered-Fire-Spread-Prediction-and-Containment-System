from fastapi import APIRouter

from .admin_dashboard import router as dashboard_router
from .fire_reports import router as fire_router
from .analytics import router as analytics_router
from .role_requests import router as role_request_router

router = APIRouter()
router.include_router(dashboard_router)
router.include_router(fire_router)
router.include_router(analytics_router)
router.include_router(role_request_router)
