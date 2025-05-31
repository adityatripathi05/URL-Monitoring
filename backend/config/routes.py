# backend/config/routes.py
from fastapi import APIRouter

# Import necessary functions and schemas from our modules
from apps.auth.routes import router as auth_router

api_router = APIRouter()

# Include app-specific routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
# api_router.include_router(monitoring_router, prefix="/monitoring", tags=["Monitoring"]) # Example

@api_router.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "message": "API is operational from config/routes.py"}
