from fastapi import APIRouter
from .location import router as location_router
from .notifications import router as notifications_router
from .geo.water_bodies import router as water_bodies_router

router = APIRouter()
router.include_router(location_router)
router.include_router(notifications_router)
router.include_router(water_bodies_router)
