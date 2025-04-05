# backend\apps\monitoring\routers\v1.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from apps.monitoring import schemas, services
from config.database import AsyncSessionLocal

router = APIRouter()

async def get_db() -> AsyncSession:
    """
    Dependency to get an asynchronous database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@router.post("/", response_model=schemas.HTTPCheck, summary="Create a new HTTP check")
async def create_http_check(http_check: schemas.HTTPCheckCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new HTTP check in the database.
    """
    return await services.create_http_check(db=db, http_check=http_check)

@router.get("/", response_model=list[schemas.HTTPCheck], summary="Read HTTP checks")
async def read_http_checks(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Read HTTP checks from the database with pagination.
    """
    http_checks = await services.get_http_checks(db, skip=skip, limit=limit)
    return http_checks

@router.get("/{http_check_id}", response_model=schemas.HTTPCheck, summary="Read HTTP check by ID")
async def read_http_check(http_check_id: int, db: AsyncSession = Depends(get_db)):
    """
    Read an HTTP check from the database by its ID.
    """
    db_http_check = await services.get_http_check(db, http_check_id=http_check_id)
    if db_http_check is None:
        return {"error": "HTTPCheck not found"}
    return db_http_check
