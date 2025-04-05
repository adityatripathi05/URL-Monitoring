# backend\main.py
from fastapi import FastAPI
from config.routes import router as api_router
from utils.logging import logger

app = FastAPI()

app.include_router(api_router)

logger.info("Application started")
