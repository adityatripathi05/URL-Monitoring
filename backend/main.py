# backend\main.py
from fastapi import FastAPI
from fastapi_utilities import repeat_every

# from utils.app_logging import logger # REMOVE THIS
from config.logging import setup_logging, get_logger # ADD THIS
from config.database import database
from config.settings import settings # Ensure settings is imported before setup_logging if it depends on it
from utils.db_migrations import apply_migrations
from apps.auth.routes import router as auth_router # Import the auth router

# Call setup_logging() early, but ensure settings are loaded.
# If settings are loaded upon import of config.settings, this is fine.
setup_logging() # ADD THIS
logger = get_logger(__name__) # ADD THIS, or specific name like "main_app"

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    logger.info("Running database migrations...")
        # Check for a strong JWT_SECRET_KEY
    if settings.environment != "development" and settings.JWT_SECRET_KEY == "default_super_secret_key_change_me":
        logger.error("JWT_SECRET_KEY is not set to a secure value. Update the .env file.")
        raise RuntimeError("JWT_SECRET_KEY must be set to a secure value in production.")
    try:
        await apply_migrations()
        logger.info("Database migrations finished successfully.")
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        # Consider more robust error handling here, e.g., exiting the application

@app.on_event("startup")
@repeat_every(seconds=3600)  # Run every hour
async def cleanup_expired_tokens():
    """
    Periodically cleans up expired tokens from the token_blacklist table.
    """
    logger.info("Running expired token cleanup...")
    async with database.pool.acquire() as conn:
        try:
            await conn.execute("DELETE FROM token_blacklist WHERE expires_at < NOW();")
            logger.info("Expired tokens cleaned up successfully.")
        except Exception as e:
            logger.error(f"Error during token cleanup: {e}")

@app.on_event("shutdown")
async def on_shutdown():
    await database.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include the authentication router
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

logger.info("Application started with Structlog")
