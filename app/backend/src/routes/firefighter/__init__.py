from fastapi import APIRouter

from .fire_reports import router as fire_reports_router
from .firefighter_dashboard import router as dashboard_router
from .fire_terrain_bias import router as terrain_bias_router

router = APIRouter()
router.include_router(fire_reports_router)
router.include_router(dashboard_router)
router.include_router(terrain_bias_router)
