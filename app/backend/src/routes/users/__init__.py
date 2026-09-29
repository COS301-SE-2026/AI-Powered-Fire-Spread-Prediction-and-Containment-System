from fastapi import APIRouter

from .fire_reports import router as fire_report_router
from .resources import router as resource_router
from .profile import router as profile_router
from .role_request import router as role_request_router
from .saved_location import router as saved_location_router

router = APIRouter()
router.include_router(fire_report_router)
router.include_router(resource_router)
router.include_router(profile_router)
router.include_router(role_request_router)
router.include_router(saved_location_router)