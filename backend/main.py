# backend\main.py
from fastapi import FastAPI
from utils.logging import logger

app = FastAPI()

logger.info("Application started")
