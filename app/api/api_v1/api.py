from fastapi import APIRouter
from .endpoints import default
from .endpoints import login

router = APIRouter()
router.include_router(default.router, prefix="/v1", tags=["v1"])
router.include_router(login.router, prefix="/v1", tags=["v1"])