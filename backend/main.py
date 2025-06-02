# backend\main.py
from fastapi import FastAPI, Depends
from fastapi_utilities import repeat_every
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import aioredis

# Import necessary functions and schemas from our modules
from config.logging_util import setup_logging, get_logger
from config.lifespan import lifespan
from config.database import database # Keep for cleanup_expired_tokens
from config.routes import api_router
from config.settings import settings

# Call setup_logging() early, but ensure settings are loaded.
# This should be called once per application lifecycle.
# If config.logging_util.setup_logging() was already called, ensure this is idempotent or called only here.
# For simplicity, assuming it's called here as the primary point if not already done in config.logging_util itself.
setup_logging()
# Initialize logger
logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
    )

@app.on_event("startup")
async def startup_event():
    redis = await aioredis.from_url(settings.RATE_LIMIT_REDIS_URL, encoding="utf8", decode_responses=True)
    await FastAPILimiter.init(redis)
    logger.info(f"Rate limiter initialized with Redis at {settings.RATE_LIMIT_REDIS_URL}")

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

logger.info("FastAPI application instance created. Routers included from config. Lifespan manager will handle startup/shutdown events.")
