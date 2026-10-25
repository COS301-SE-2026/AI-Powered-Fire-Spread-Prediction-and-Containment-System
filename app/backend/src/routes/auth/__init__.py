from fastapi import APIRouter

from .login import router as login_router
from .logout import router as logout_router
from .register import router as register_router
from .two_factor import router as two_fac_router
from .edit_password import router as edit_password_router
from .two_factor_toggle import router as two_factor_toggle_router

router = APIRouter()
router.include_router(login_router)
router.include_router(logout_router)
router.include_router(register_router)
router.include_router(two_fac_router)
router.include_router(edit_password_router)
router.include_router(two_factor_toggle_router)
