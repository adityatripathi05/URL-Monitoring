import sys
import os
import asyncpg
from passlib.context import CryptContext
import asyncio
from dotenv import load_dotenv
import argparse # Added argparse

# Import necessary functions and schemas from our modules
from project_config.logging_util import get_logger
from utils.db_utils import fetch_one

# Initialize logger
logger = get_logger(__name__)

# Configure passlib context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_db_connection():
    """Establishes and returns an asyncpg database connection."""
    # Load environment variables from .env file two levels up
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir)) # Two levels up
    env_path = os.path.join(project_root, '.env')
    load_dotenv(dotenv_path=env_path)

    required_vars = ["DB_USER", "DB_PASSWORD", "DB_NAME", "DB_HOST", "DB_PORT"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        logger.error(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        logger.error(f"Attempted to load .env from: {os.path.abspath(env_path)}")
        sys.exit(1)

    try:
        conn = await asyncpg.connect(
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME"),
            host=os.environ.get("DB_HOST"),
            port=int(os.environ.get("DB_PORT", 5432)),
        )
        logger.info("Database connection established successfully.")
        return conn
    except asyncpg.PostgresError as e:
        logger.error(f"Database connection error: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Database connection configuration error: {e}")
        sys.exit(1)

async def get_admin_role_id(conn: asyncpg.Connection):
    """Fetches the ID of the 'Admin' role from the roles table."""
    try:
        admin_role_row = await fetch_one(conn, "SELECT id FROM roles WHERE name = 'Admin'")
        if not admin_role_row:
            logger.error("Admin role not found. Ensure migrations are applied and the 'Admin' role exists.")
            raise ValueError("Admin role not found.")
        admin_role_id = admin_role_row['id']
        logger.info(f"Admin role ID '{admin_role_id}' fetched successfully.")
        return admin_role_id
    except Exception as e:
        logger.error(f"Error fetching admin role ID: {e}")
        raise

async def create_user(conn: asyncpg.Connection, username: str, email: str, password: str, role_id: int):
    """Creates a new user in the database."""
    try:
        hashed_password = pwd_context.hash(password)
        await conn.execute(
            """
            INSERT INTO users (username, email, password, role_id)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (email) DO NOTHING;
            """,
            username,
            email,
            hashed_password,
            role_id
        )
        # Check if user was actually inserted or already existed
        user_check = await fetch_one(conn, "SELECT id FROM users WHERE email = $1", email)
        if user_check:
            logger.info(f"User '{username}' with email '{email}' ensured in database (either created or already existed).")
        else:
            # This case might occur if ON CONFLICT DO NOTHING was triggered by a different constraint or an unexpected issue.
            logger.warning(f"User '{username}' with email '{email}' was not found after insert attempt. It might already exist with a different email or another issue occurred.")
    except Exception as e:
        logger.error(f"Error creating user '{username}': {e}")
        # Not raising here to allow the main script to potentially continue or handle cleanup

async def update_user(conn: asyncpg.Connection, email: str, new_username: str = None, new_password: str = None) -> bool:
    """Updates an existing user's username and/or password if they are an admin."""
    try:
        user = await fetch_one(conn, "SELECT id, username, role_id FROM users WHERE email = $1", email)
        if not user:
            logger.error(f"User with email {email} not found.")
            return False

        admin_role_id = await get_admin_role_id(conn) # This can raise ValueError if 'Admin' role not found

        if user['role_id'] != admin_role_id:
            logger.error(f"User {email} (ID: {user['id']}) is not an admin (Role ID: {user['role_id']}, Expected Admin Role ID: {admin_role_id}). Update aborted.")
            return False

        update_fields = []
        params = []
        param_idx = 1

        if new_username and new_username.strip():
            update_fields.append(f"username = ${param_idx}")
            params.append(new_username.strip())
            param_idx += 1

        if new_password and new_password.strip():
            hashed_password = pwd_context.hash(new_password.strip())
            update_fields.append(f"password = ${param_idx}")
            params.append(hashed_password)
            param_idx += 1

        if not update_fields:
            logger.info(f"No changes requested for user {email}.")
            return True

        query = f"UPDATE users SET {', '.join(update_fields)} WHERE email = ${param_idx}"
        params.append(email)

        await conn.execute(query, *params)
        logger.info(f"User {email} updated successfully with new details.")
        return True

    except ValueError as ve: # Catching ValueError from get_admin_role_id
        logger.error(f"Error preparing to update user {email}: {ve}")
        return False
    except Exception as e:
        logger.error(f"Error updating user {email}: {e}")
        return False

async def create_super_admin():
    """Main function to create a super admin user."""
    conn = None
    email = None  # Initialize email to None for logging in finally block
    try:
        logger.info("Starting super admin creation process...")
        conn = await get_db_connection()
        admin_role_id = await get_admin_role_id(conn)

        username = input("Enter username for the super admin: ")
        email = input("Enter email for the super admin: ")
        password = input("Enter password for the super admin: ")

        await create_user(conn, username, email, password, admin_role_id)
        logger.info(f"Super admin creation process for {email} completed.")

    except ValueError as ve: # Specifically catch ValueError from get_admin_role_id
        logger.error(f"Setup error: {ve}")
        if email: # Log email if available
            logger.error(f"Super admin creation process for {email} failed during setup.")
        else:
            logger.error("Super admin creation process failed during setup before email was provided.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during super admin creation: {e}")
        if email: # Log email if available
            logger.error(f"Super admin creation process for {email} failed.")
        else:
            logger.error("Super admin creation process failed before email was provided.")
    finally:
        if conn:
            try:
                await conn.close()
                logger.info("Database connection closed.")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")

async def update_super_admin_interactive():
    """Interactive way to update a super admin's details."""
    conn = None
    email_to_update = None
    try:
        logger.info("Starting super admin update process...")
        conn = await get_db_connection()

        email_to_update = input("Enter the email of the super admin to update: ").strip()
        if not email_to_update:
            logger.warning("Email cannot be empty. Exiting update process.")
            return

        new_username = input("Enter new username (or press Enter to keep current): ").strip()
        new_password = input("Enter new password (or press Enter to keep current): ").strip()

        if not new_username and not new_password:
            logger.info("No changes requested. Exiting update process.")
            return

        success = await update_user(conn, email_to_update, new_username or None, new_password or None)

        if success:
            logger.info(f"Super admin {email_to_update} update process completed successfully.")
        else:
            logger.warning(f"Super admin {email_to_update} update process encountered issues. Check logs above.")

    except Exception as e:
        logger.error(f"An error occurred during the super admin update process for {email_to_update or 'unknown email'}: {e}")
    finally:
        if conn:
            try:
                await conn.close()
                logger.info("Database connection closed after update attempt.")
            except Exception as e:
                logger.error(f"Error closing database connection after update attempt: {e}")


async def main():
    parser = argparse.ArgumentParser(description="Manage super admin users.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # Create Sub-parser
    parser_create = subparsers.add_parser("create", help="Create a new super admin user.")
    parser_create.set_defaults(func=create_super_admin)

    # Update Sub-parser
    parser_update = subparsers.add_parser("update", help="Update an existing super admin user.")
    parser_update.set_defaults(func=update_super_admin_interactive)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        await args.func()  # Call the appropriate async function
    else:
        # This part should ideally not be reached if 'dest' and 'required=True' are set for subparsers
        # and no default function is set for the main parser.
        # If a default function for the main parser was desired, it would be set via parser.set_defaults(func=...)
        logger.info("No command provided, printing help.")
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
