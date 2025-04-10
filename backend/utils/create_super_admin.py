import asyncpg
import os
# import bcrypt # No longer needed directly
from passlib.context import CryptContext # Import passlib
import asyncio
from dotenv import load_dotenv
import sys

# Configure passlib context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_super_admin():
    """Creates a super admin user in the database with interactive prompts."""

    conn = None
    try:
        # Load environment variables from .env file relative to the script's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir) # Assumes utils is one level down from backend root
        env_path = os.path.join(project_root, '../.env') # Assumes .env is at the project root
        load_dotenv(dotenv_path=env_path)

        # Check essential env vars
        required_vars = ["DB_USER", "DB_PASSWORD", "DB_NAME", "DB_HOST", "DB_PORT"]
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
            print(f"Attempted to load .env from: {os.path.abspath(env_path)}")
            sys.exit(1)

        # Remove bcrypt dependency check

        conn = await asyncpg.connect(
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME"),
            host=os.environ.get("DB_HOST"),
            port=int(os.environ.get("DB_PORT", 5432)),
        )

        # Get Admin role ID
        admin_role_id_row = await conn.fetchrow("SELECT id FROM roles WHERE name = 'Admin'")
        if not admin_role_id_row:
            raise Exception("Admin role not found. Ensure migrations are applied and the 'Admin' role exists.")
        admin_role_id = admin_role_id_row['id']

        # Prompt for user details
        username = input("Username for the super admin user: ")
        email = input("Email for the super admin user: ")
        password = input("Password for the super admin user: ")

        # Hash password using passlib
        hashed_password = pwd_context.hash(password)

        # Insert super admin user
        await conn.execute(
            """
            INSERT INTO users (username, email, password, role_id)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (email) DO NOTHING; -- Avoid error if user already exists
            """,
            username,
            email,
            hashed_password,
            admin_role_id
        )

        # Check if user was actually inserted (or already existed)
        user_check = await conn.fetchrow("SELECT id FROM users WHERE email = $1", email)
        if user_check:
             print(f"Super admin user '{username}' with email '{email}' ensured in database.")
        else:
             # This case should ideally not happen with ON CONFLICT DO NOTHING unless there's another issue
             print(f"Failed to ensure super admin user '{username}' creation.")


    except Exception as e:
        print(f"Error creating super admin user: {e}")
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(create_super_admin())
