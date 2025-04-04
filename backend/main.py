# backend\main.py
from fastapi import FastAPI
from config.routes import router as api_router

app = FastAPI()

app.include_router(api_router)
