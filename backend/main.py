# backend\main.py
# backend\main.py
from fastapi import FastAPI

from utils.app_logging import logger
from config.database import database
from utils.db_migrations import apply_migrations

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logger.info("Running database migrations...")
    try:
        await apply_migrations()
        logger.info("Database migrations finished successfully.")
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        # Consider more robust error handling here, e.g., exiting the application

@app.on_event("shutdown")
async def on_shutdown():
    await database.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

logger.info("Application started")
