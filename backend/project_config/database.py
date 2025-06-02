# backend\config\database.py
import asyncio
import asyncpg
from typing import Dict

# Import necessary functions and schemas from our modules
from project_config.logging_util import get_logger
from project_config.settings import settings

# Initialize logger
logger = get_logger(__name__)

# Database configuration settings from environment variables
DB_CONFIG = {
    "host": settings.DB_HOST,
    "database": settings.DB_NAME,
    "user": settings.DB_USER,
    "password": settings.DB_PASSWORD,
    "port": settings.DB_PORT
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

    async def initialize(self):
        """
        Initializes the database connection pool.
        """
        if self.pool is None:
            try:
                self.pool = await asyncpg.create_pool(**self.db_config, min_size=1, max_size=20)
                logger.info("Database connection pool initialized")
            except Exception as e:
                logger.error(f"Error initializing database connection pool: {e}")
                raise

        return self

    async def close(self):
        """
        Closes the database connection pool.
        """
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")


# Global database instance
database = Database(DB_CONFIG)
