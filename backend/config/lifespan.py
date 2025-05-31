# backend/config/lifespan.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.config.database import database  # Assuming database object is in config.database
from backend.config.settings import settings
from backend.config.logging import get_logger # Using Structlog logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Phase ---
    logger.info("Application startup sequence initiated...")

    # JWT Secret Check
    if settings.ENVIRONMENT != "development" and settings.JWT_SECRET_KEY == "default_super_secret_key_change_me":
        logger.error("FATAL: JWT_SECRET_KEY is not set to a secure value. Update the .env file.")
        # Raising an error here will prevent FastAPI from starting up if the key is insecure in non-dev environments.
        raise RuntimeError("JWT_SECRET_KEY must be set to a secure value in production.")
    else:
        logger.info("JWT_SECRET_KEY check passed.")

    # Initialize Database Pool (explicitly, if desired)
    # The current database.py initializes pool on Database object creation or first use.
    # Explicitly calling an initialize method here can make startup sequence clearer.
    # For now, we assume database.pool is available when needed.
    # If database.initialize() exists and is idempotent, it could be called here.
    # Example: await database.initialize() # if you add such a method to your Database class
    logger.info("Database pool should be available (managed by config.database).")


    # Note: Database migrations are now handled by Alembic CLI, so no migration call here.
    # Note: The @repeat_every task for cleanup_expired_tokens in main.py will
    #       start automatically when the asyncio loop is running (after this startup phase).

    logger.info("Application startup complete. Ready to serve requests.")
    yield
    # --- Shutdown Phase ---
    logger.info("Application shutdown sequence initiated...")
    if database.pool:  # Check if pool was initialized
        try:
            await database.close()
            logger.info("Database connection pool closed successfully.")
        except Exception as e:
            logger.error("Error closing database connection pool.", exc_info=True)
    else:
        logger.info("Database pool was not initialized or already closed.")
    logger.info("Application shutdown complete.")
