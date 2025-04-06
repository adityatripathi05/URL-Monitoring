# backend\config\database.py
import asyncio
import logging
import os
import asyncpg
from typing import Dict


# Configure logging
logger = logging.getLogger(__name__)

# Database configuration settings from environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT"))
}


class Database:
    """
    Manages the asyncpg database connection pool.
    """

    def __init__(self, db_config: Dict[str, str]):
        """
        Initializes the Database object with the given configuration.
        Args:
            db_config (Dict[str, str]): Database configuration parameters.
        """
        if not all(key in db_config for key in ['host', 'database', 'user', 'password']):
            raise ValueError("Missing required database configuration parameters")
        self.db_config = db_config
        self.pool = None
        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        """
        Initializes the database connection pool.
        """
        if self.pool is None:
            try:
                self.pool = await asyncpg.create_pool(**self.db_config, min_size=1, max_size=20)
                self.logger.info("Database connection pool initialized")
            except Exception as e:
                self.logger.error(f"Error initializing database connection pool: {e}")
                raise

        return self

    async def close(self):
        """
        Closes the database connection pool.
        """
        if self.pool:
            await self.pool.close()
            self.logger.info("Database connection pool closed")


# Global database instance
database = Database(DB_CONFIG)


async def get_db_connection():
    """
    Asynchronous dependency that yields a database connection from the pool.
    """
    await database.initialize()
    try:
        yield database
    finally:
        pass  # Don't close pool here as it's shared
