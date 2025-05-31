# backend\main.py
from fastapi import FastAPI
from fastapi_utilities import repeat_every

# from utils.app_logging import logger # REMOVE THIS
from config.logging import setup_logging, get_logger # ADD THIS
from backend.config.lifespan import lifespan # ADD THIS
from config.database import database # Keep for cleanup_expired_tokens
# from config.settings import settings # No longer needed directly in main.py for startup checks
# from utils.db_migrations import apply_migrations # REMOVE THIS
from apps.auth.routes import router as auth_router # Import the auth router

# Call setup_logging() early, but ensure settings are loaded.
# This should be called once per application lifecycle.
# If config.logging.setup_logging() was already called, ensure this is idempotent or called only here.
# For simplicity, assuming it's called here as the primary point if not already done in config.logging itself.
setup_logging()
logger = get_logger(__name__)

app = FastAPI(lifespan=lifespan) # MODIFIED HERE

# OLD STARTUP AND SHUTDOWN FUNCTIONS ARE REMOVED
# @app.on_event("startup")
# async def startup_event(): ... (Removed - logic moved to lifespan)

# @app.on_event("shutdown")
# async def on_shutdown(): ... (Removed - logic moved to lifespan)


# This task will be managed by fastapi-utilities once the app is running
@repeat_every(seconds=3600, logger=logger, wait_first=True) # Added logger and wait_first
async def cleanup_expired_tokens():
    """
    Periodically cleans up expired tokens from the token_blacklist table.
    """
    logger.info("Running expired token cleanup task...")
    if database.pool: # Check if pool is initialized
        try:
            # asyncpg.pool.Pool.acquire is a context manager
            async with database.pool.acquire() as conn:
                await conn.execute("DELETE FROM token_blacklist WHERE expires_at < NOW();")
                logger.info("Expired tokens cleaned up successfully.")
        except Exception as e:
            logger.error("Error during token cleanup.", exc_info=True) # Use exc_info for details
    else:
        logger.warning("Token cleanup skipped: Database pool not available.")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include the authentication router
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

logger.info("FastAPI application instance created. Lifespan manager will handle startup/shutdown events.")
