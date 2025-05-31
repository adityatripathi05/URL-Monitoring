import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
# from sqlalchemy import pool # Not strictly needed if using create_async_engine directly for connectable

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line needs to be compatible with your logging setup.
# If using structlog primarily, you might not need fileConfig if structlog handles stdlib.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import settings to get database URL (adjust import path as needed)
# This assumes settings.py can be imported like this from alembic's execution context
import os, sys
# Ensure the backend directory is in sys.path to find the 'config' module
# __file__ is backend/alembic/env.py, so dirname(__file__) is backend/alembic
# dirname(dirname(__file__)) is backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import settings

# Set target_metadata to None if not using SQLAlchemy models for autogenerate
target_metadata = None

def get_db_url():
    return f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

# Update sqlalchemy.url in the config object
config.set_main_option('sqlalchemy.url', get_db_url())

def run_migrations_offline():
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Use a synchronous connection for offline mode if required by some operations
        # For raw SQL execution, this might not be strictly necessary but is safer
        # as_sql=True, # This can be useful for generating SQL scripts
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    # For raw SQL migrations, we don't need transactions managed by Alembic's context
    # if our SQL scripts handle their own transactions.
    # However, begin_transaction() is generally good practice.
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        # poolclass=pool.NullPool, # Recommended for Alembic async to avoid event loop issues
                                  # However, create_async_engine handles this differently.
                                  # NullPool is more for traditional sync engines with Alembic async.
                                  # Default pooling should be fine with create_async_engine.
    )

    async with connectable.connect() as connection:
        # For raw SQL, we need to make sure run_sync is not trying to manage
        # transactions in a way that conflicts with manual SQL execution.
        # The do_run_migrations function should handle the transaction block.
        await connection.run_sync(do_run_migrations)

    # Dispose of the engine when done
    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
