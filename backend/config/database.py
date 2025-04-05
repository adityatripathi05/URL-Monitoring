# backend\config\database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Database connection details from environment variables
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")
DB_PORT = os.environ.get("DB_PORT")

# Construct the database URL for asyncpg
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@db:{DB_PORT}/{DB_NAME}"

# Connection pool settings from environment variables
pool_size = int(os.environ.get("DB_POOL_SIZE", 5))
max_overflow = int(os.environ.get("DB_MAX_OVERFLOW", 10))
pool_recycle = int(os.environ.get("DB_POOL_RECYCLE", 3600))

# Create an asynchronous engine with connection pooling
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, pool_size=pool_size, max_overflow=max_overflow, pool_recycle=pool_recycle)

# Asynchronous session maker
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for declarative models
Base = declarative_base()
