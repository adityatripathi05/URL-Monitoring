# backend/apps/auth/services.py
from datetime import datetime
import asyncpg
from fastapi import HTTPException, status
from typing import Union

# Import necessary functions and schemas from our modules
from backend.config.logging import get_logger
from utils.db_utils import fetch_one, get_db_connection
from apps.auth.security import verify_password
from apps.auth.schemas import UserOut, UserInDB

# Initialize logger
logger = get_logger(__name__)


# --- Custom Exceptions (Keep existing) ---
class UserNotFound(Exception):
    """Custom exception for user not found."""
    pass

class InvalidPassword(Exception):
    """Custom exception for invalid password."""
    pass


# --- Token Blacklist Management ---
#
# The `token_blacklist` table stores JTIs of tokens that have been invalidated
# (e.g., due to logout). Each entry includes an `expires_at` timestamp, which
# corresponds to the original expiration time of the blacklisted token.
#
# IMPORTANT: Periodic Cleanup Required
# To prevent the `token_blacklist` table from growing indefinitely with expired
# JTIs, a cleanup mechanism must be implemented. This mechanism should periodically
# remove entries where the `expires_at` timestamp is in the past.
#
# Example SQL for cleanup (adjust for your specific SQL dialect if necessary,
#                         NOW() is common for PostgreSQL):
# DELETE FROM token_blacklist WHERE expires_at < NOW();
#
# This cleanup can be implemented as:
# - A cron job running at regular intervals (e.g., daily).
# - A scheduled task within the application if using a task scheduler (e.g., APScheduler, Celery).
#
# Regularly cleaning this table ensures optimal performance and manages database size.

async def is_token_blacklisted(jti: str):
    """
    Checks if a token (by jti) is blacklisted in the database.
    """
    conn = None
    try:
        conn = await get_db_connection()
        result = await fetch_one(conn, "SELECT jti FROM token_blacklist WHERE jti = $1", jti)
        return result is not None # Returns True if jti found (blacklisted)
    except Exception as e:
        logger.error(f"Database error checking token blacklist: {e}")
        return False # Assume not blacklisted on DB error for safety (or raise exception)
    finally:
            if conn:
                await conn.close()


async def blacklist_token(jti: str, expires_at: datetime, db: any):
    """
    Blacklists a token by adding its jti and expiry to the token_blacklist table.
    """
    try:
        await db.execute(
            "INSERT INTO token_blacklist (jti, expires_at) VALUES ($1, $2)",
            jti, expires_at
        )
        logger.info(f"Token with JTI {jti} blacklisted successfully.")
    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"Database error blacklisting token with JTI {jti}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not blacklist token due to a server error."
        )

class InvalidPassword(Exception):
    """Custom exception for invalid password."""
    pass


async def get_user_by_email(email: str) -> Union[UserInDB, None]:
    """Fetches a user from the database by email and returns UserInDB object."""
    conn = None
    try:
        conn = await get_db_connection()
        user_row = await fetch_one(
            conn,
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
            user_data['password'] = user_data.pop('hashed_password')
            user_data['role'] = user_data.pop('role_name')
            return UserInDB(**user_data)
        return None
    finally:
        if conn:
            await conn.close()


async def authenticate_user(email: str, password: str) -> UserOut:
    """
    Authenticates a user by email and password.

    Raises:
        UserNotFound: If the user with the given email does not exist.
        InvalidPassword: If the password does not match.

    Returns:
        UserOut object if authentication is successful.
    """
    user_in_db = await get_user_by_email(email)
    if not user_in_db:
        raise UserNotFound("User not found")

    if not verify_password(password, user_in_db.password): # Compare against fetched hashed password
        raise InvalidPassword("Invalid password")

    return UserOut(**user_in_db.model_dump())
