# backend\config\routes.py
from fastapi import APIRouter
from apps.monitoring.routers import v1 as monitoring_router

router = APIRouter()

router.include_router(monitoring_router.router, prefix="/monitoring", tags=["monitoring"])
