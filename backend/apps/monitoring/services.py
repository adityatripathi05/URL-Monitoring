# backend\apps\monitoring\services.py
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas
from sqlalchemy import select

async def get_http_check(db: AsyncSession, http_check_id: int):
    """
    Get an HTTP check from the database by its ID.
    """
    result = await db.execute(select(models.HTTPCheck).filter(models.HTTPCheck.id == http_check_id))
    return result.scalars().first()

async def get_http_checks(db: AsyncSession, skip: int = 0, limit: int = 100):
    """
    Get a list of HTTP checks from the database with pagination.
    """
    result = await db.execute(select(models.HTTPCheck).offset(skip).limit(limit))
    return result.scalars().all()

async def create_http_check(db: AsyncSession, http_check: schemas.HTTPCheckCreate):
    """
    Create a new HTTP check in the database.
    """
    db_http_check = models.HTTPCheck(**http_check.model_dump())
    db.add(db_http_check)
    await db.commit()
    await db.refresh(db_http_check)
    return db_http_check
