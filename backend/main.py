# backend\main.py
from fastapi import FastAPI, Depends
from fastapi_utilities import repeat_every
from fastapi_limiter.depends import RateLimiter

# Import necessary functions and schemas from our modules
from project_config.logging_util import setup_logging, get_logger
from project_config.lifespan import lifespan
from project_config.database import database # Keep for cleanup_expired_tokens
from project_config.routes import api_router
from project_config.settings import settings

# Call setup_logging() early, but ensure settings are loaded.
# This should be called once per application lifecycle.
# If project_config.logging_util.setup_logging() was already called, ensure this is idempotent or called only here.
# For simplicity, assuming it's called here as the primary point if not already done in project_config.logging_util itself.
setup_logging()
# Initialize logger
logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
    )

# This task will be managed by fastapi-utilities once the app is running
@repeat_every(seconds=3600, logger=logger, wait_first=True)
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

# Example: Apply global rate limit to all routes (can be overridden per route)
app.include_router(
    api_router,
    dependencies=[Depends(RateLimiter(times=int(settings.GLOBAL_RATE_LIMIT.split('/')[0]), seconds=60))]
)

logger.info("FastAPI application instance created. Routers included from project_config. Lifespan manager will handle startup/shutdown events.")
