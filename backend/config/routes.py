# backend/config/routes.py
from fastapi import APIRouter
from backend.apps.auth.routes import router as auth_router
# Import other app routers here as they are created
# from backend.apps.monitoring.routes import router as monitoring_router # Example

api_router = APIRouter()

# Include app-specific routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
# api_router.include_router(monitoring_router, prefix="/monitoring", tags=["Monitoring"]) # Example

@api_router.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "message": "API is operational from config/routes.py"}
