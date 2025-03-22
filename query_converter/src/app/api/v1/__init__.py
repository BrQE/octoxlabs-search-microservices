from fastapi import APIRouter

from .health_route import router as health_router
from .query_route import router as query_router

router = APIRouter(prefix="/v1")
router.include_router(health_router)
router.include_router(query_router)