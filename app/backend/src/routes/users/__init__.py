from fastapi import APIRouter

from .fire_reports import router as fire_report_router
from .resources import router as resource_router

router = APIRouter()
router.include_router(fire_report_router)
router.include_router(resource_router)
