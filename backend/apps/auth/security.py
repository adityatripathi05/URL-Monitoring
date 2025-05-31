# backend/apps/auth/security.py
from datetime import datetime, timedelta
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext  # Import CryptContext

from config.settings import settings # Import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Use the same context

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "type": "access", "jti": uuid.uuid4().hex}) # Add jti claim
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm) # Use settings

def create_refresh_token(data: dict):
    """Creates a refresh token with a longer expiry."""
    to_encode = data.copy()
    # Use refresh token expiry from settings
    expire = datetime.utcnow() + settings.refresh_token_expires
    to_encode.update({"exp": expire, "type": "refresh", "jti": uuid.uuid4().hex}) # Add jti claim
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password) # Use pwd_context

def hash_password(password: str) -> str:
    return pwd_context.hash(password) # Use pwd_context

def decode_token(token: str):
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]) # Use settings
    except JWTError:
        return None
