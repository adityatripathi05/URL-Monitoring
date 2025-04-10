# backend/utils/db_migrations.py
import os

import asyncpg
import asyncio  # Import asyncio for sleep

from utils.app_logging import logger
from utils.db_utils import fetch_all
from config.database import DB_CONFIG

async def apply_migrations():
    """Applies pending SQL migrations to the database with retry logic."""
    logger.info("Applying database migrations...")

    conn = None
    retries = 15  # Maximum retry attempts
    delay = 2     # Delay between retries in seconds

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Database connection attempt {attempt}/{retries}...") # Log attempt number
            conn = await asyncpg.connect(**DB_CONFIG)
            logger.info("Database connection successful.") # Log successful connection
            break  # Connection successful, exit retry loop
        except Exception as e:
            logger.warning(f"Database connection failed: {e}") # Log connection failure
            if attempt == retries:
                logger.error("Max retries reached. Aborting migrations.") # Log max retries reached
                raise  # Re-raise the exception after max retries
            else:
                logger.info(f"Retrying in {delay} seconds...") # Log retry delay
                await asyncio.sleep(delay)  # Wait before retrying

    if conn is None: # Should not happen, but for extra safety
        raise Exception("Failed to connect to database after multiple retries")

    # --- Migration Tracking Table Check and Creation ---
    logger.info("Checking/creating migration tracking table...")
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            migration_id VARCHAR(255) PRIMARY KEY,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)

    # --- Get Applied Migrations ---
    logger.info("Fetching already applied migrations...")
    applied_migrations = set()
    rows = await fetch_all(conn, "SELECT migration_id FROM _migrations;")
    for row in rows:
        applied_migrations.add(row['migration_id'])
    logger.debug(f"Already applied migrations: {applied_migrations}")

    # --- Read Migration Files ---
    logger.info("Reading migration files...")
    migration_files = []
    migrations_dir = os.path.join(os.path.dirname(__file__), '../migrations') # migrations dir relative to current file
    for filename in sorted(os.listdir(migrations_dir)): # sorted to apply in order
        if filename.endswith(".sql"):
            migration_files.append(filename)
    logger.debug(f"Found migration files: {migration_files}")

    # --- Apply New Migrations ---
    logger.info("Applying new migrations...")
    for filename in migration_files:
        if filename not in applied_migrations:
            migration_path = os.path.join(migrations_dir, filename)
            logger.info(f"Applying migration: {filename}")
            try:
                async with conn.transaction():  # Wrap in a transaction
                    with open(migration_path, 'r') as f:
                        sql_script = f.read()
                    await conn.execute(sql_script)
                    await conn.execute(
                        "INSERT INTO _migrations (migration_id) VALUES ($1);", filename
                    )
                    logger.info(f"Migration {filename} applied successfully.")
            except Exception as e:
                logger.error(f"Error applying migration {filename}: {e}")
                raise
        else:
            logger.info(f"Migration {filename} already applied, skipping.")
    await conn.close()
    logger.info("Database migrations completed.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(apply_migrations())
