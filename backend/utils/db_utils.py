from asyncpg import Connection

# Import necessary functions and schemas from our modules
from config.logging import get_logger
from config.database import database

logger = get_logger(__name__)

async def get_db_connection():
    """
    Asynchronous dependency that yields a database connection from the pool.
    """
    await database.initialize()
    async with database.pool.acquire() as connection:
        yield connection

async def execute_query(conn: Connection, query: str, *args):
    """
    Executes a database query with error handling.
    """
    try:
        return await conn.execute(query, *args)
    except Exception as e:
        logger.error(f"Error executing query: {query} with args: {args}. Error: {e}")
        raise

async def fetch_one(conn: Connection, query: str, *args):
    """
    Fetches a single row from the database with error handling.
    """
    try:
        return await conn.fetchrow(query, *args)
    except Exception as e:
        logger.error(f"Error fetching row: {query} with args: {args}. Error: {e}")
        raise

async def fetch_all(conn: Connection, query: str, *args):
    """
    Fetches multiple rows from the database with error handling.
    """
    try:
        return await conn.fetch(query, *args)
    except Exception as e:
        logger.error(f"Error fetching rows: {query} with args: {args}. Error: {e}")
        raise