from fastapi import APIRouter
from .endpoints import default
from .endpoints import MySQL
from .endpoints import DynamoDB
from .endpoints import DBMSattendance

router = APIRouter()
router.include_router(default.router, prefix="/v1", tags=["v1"])
router.include_router(MySQL.router, prefix="/v1", tags=["v1"])
router.include_router(DynamoDB.router, prefix="/v1", tags=["v1"])
router.include_router(DBMSattendance.router, prefix="/v1/attendance", tags=["attendance"])