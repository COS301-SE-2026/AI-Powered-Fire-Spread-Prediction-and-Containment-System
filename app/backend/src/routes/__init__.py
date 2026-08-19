from fastapi import APIRouter
from .location import router as location_router

router = APIRouter()
router.include_router(location_router)