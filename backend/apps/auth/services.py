# backend/apps/auth/services.py
from datetime import datetime

import asyncpg
from fastapi import HTTPException, status
from typing import Union

from config.settings import settings
from utils.app_logging import logger
from apps.auth.security import verify_password, decode_token
from apps.auth.schemas import UserOut, TokenData


# --- Custom Exceptions (Keep existing) ---
class UserNotFound(Exception):
    """Custom exception for user not found."""
    pass

class InvalidPassword(Exception):
    """Custom exception for invalid password."""
    pass


async def is_token_blacklisted(jti: str, db):
    """
    Checks if a token (by jti) is blacklisted in the database.
    """
    try:
        result = await db.fetch_one("SELECT jti FROM token_blacklist WHERE jti = :jti", {"jti": jti})
        return result is not None # Returns True if jti found (blacklisted)
    except Exception as e:
        logger.error(f"Database error checking token blacklist: {e}")
        return False # Assume not blacklisted on DB error for safety (or raise exception)


async def blacklist_token(token: str, db):
    """
    Blacklists a token by adding its jti to the token_blacklist table.
    """
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token format for blacklisting"
        )
    try:
        token_data = TokenData(**payload)
        if token_data.jti is None or token_data.exp is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token payload for blacklisting (missing jti or exp)"
            )

        expires_at = datetime.utcfromtimestamp(token_data.exp) # Convert exp to datetime

        await db.execute(
            "INSERT INTO token_blacklist (jti, expires_at) VALUES (:jti, :expires_at)",
            {"jti": token_data.jti, "expires_at": expires_at}
        )
    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"Database error blacklisting token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not blacklist token due to a server error"
        )

class InvalidPassword(Exception):
    """Custom exception for invalid password."""
    pass


async def get_db_connection():
    """Abstraction for getting a database connection from the pool."""
    return await asyncpg.connect(
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
    )


async def get_user_by_email(email: str) -> Union[UserOut, None]: # Changed return type to UserOut
    """Fetches a user from the database by email and returns UserOut object."""
    conn = None
    try:
        conn = await get_db_connection()
        # Modified query to select is_verified and join roles, and match schema
        user_row = await conn.fetchrow(
            """
            SELECT 
                u.id, u.username, u.email, u.password as hashed_password, 
                u.role_id, r.name as role_name, u.is_verified
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.email = $1
            """,
            email
        )
        if user_row:
            user_data = dict(user_row)
            user_data['role'] = user_data.pop('role_name') # Rename role_name to role to match UserOut
            return UserOut(**user_data)
        return None
    finally:
        if conn:
            await conn.close()


async def authenticate_user(email: str, password: str) -> UserOut: # Changed return type to UserOut
    """
    Authenticates a user by email and password.

    Raises:
        UserNotFound: If the user with the given email does not exist.
        InvalidPassword: If the password does not match.

    Returns:
        UserOut object if authentication is successful.
    """
    user = await get_user_by_email(email)
    if not user:
        raise UserNotFound("User not found")

    if not verify_password(password, user.password): # Compare against fetched hashed password
        raise InvalidPassword("Invalid password")

    return user
