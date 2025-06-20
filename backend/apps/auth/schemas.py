from uuid import UUID
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    role: str
    is_verified: bool  # Indicates if the user's email is verified

class UserInDB(UserOut):
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: str
    role: str
    exp: Optional[int] = None
    type: Optional[str] = None # Add type field to distinguish token types
    jti: Optional[str] = None  # Add jti field for token blacklist

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Schema for returning only the access token (e.g., after refresh)
class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LogoutRequest(BaseModel):
    refresh_token: str
