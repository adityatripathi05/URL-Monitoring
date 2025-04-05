# backend\config\settings.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "URL Monitoring System"
    admin_email: str = "triaditya94@gmail.com"

    class Config:
        env_file = ".env"

settings = Settings()
