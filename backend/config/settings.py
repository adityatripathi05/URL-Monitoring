# backend/config/settings.py
from pydantic_settings import BaseSettings
from datetime import timedelta
from typing import Optional

class Settings(BaseSettings):
    app_name: str
    admin_email: str
    app_version: str
    environment: str

    # Database Settings
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # Timezone configuration
    TZ: str
    # Logging Configuration
    LOG_LEVEL: str

    # JWT Settings
    JWT_SECRET_KEY: str  # Load from JWT_SECRET_KEY env var - IMPORTANT: set in .env
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int # Default 15 minutes expiration
    REFRESH_TOKEN_EXPIRE_DAYS: int
    password_reset_token_expires_hours: int
    email_verification_token_expires_hours: int

    # Role-specific access token expiry (minutes) - can be overridden by env vars (e.g., VIEWER_ACCESS_TOKEN_EXPIRES_MINUTES=120 in .env)
    admin_access_token_expires_minutes: int = 15 # Default for Admin
    viewer_access_token_expires_minutes: int = 120 # Default for Viewer (2 hours)

    # Default role
    default_role_id: str

    # SMTP Settings for email functionality
    SMTP_USER: Optional[str] = None # Optional - set in .env if email features are used
    SMTP_PASSWORD: Optional[str] = None # Optional - set in .env if email features are used
    SMTP_SERVER: str # Default SMTP server
    SMTP_PORT: int # Default SMTP port

    class Config:
        env_file = ".env"
        env_prefix = '' # Ensure env vars like DB_USER are loaded directly
        case_sensitive = False # Allow case-insensitive matching for env vars


    @property
    def access_token_expires(self):
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def refresh_token_expires(self):
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)

    @property
    def password_reset_token_expires(self):
        return timedelta(hours=self.password_reset_token_expires_hours)

    @property
    def email_verification_token_expires(self):
        return timedelta(hours=self.email_verification_token_expires_hours)

    @property
    def admin_access_token_expires(self):
        return timedelta(minutes=self.admin_access_token_expires_minutes)

    @property
    def viewer_access_token_expires(self):
        return timedelta(minutes=self.viewer_access_token_expires_minutes)


settings = Settings()

# Optional: If needed globally
def get_token_expiry_by_role(role: str) -> timedelta:
    if role == "admin":
        return settings.admin_access_token_expires
    return settings.viewer_access_token_expires
