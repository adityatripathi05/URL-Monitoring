# backend\apps\monitoring\routers\v1.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from . import schemas, services
from ...config.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.HTTPCheck)
async def create_http_check(http_check: schemas.HTTPCheckCreate, db: Session = Depends(get_db)):
    return services.create_http_check(db=db, http_check=http_check)

@router.get("/", response_model=list[schemas.HTTPCheck])
async def read_http_checks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    http_checks = services.get_http_checks(db, skip=skip, limit=limit)
    return http_checks

@router.get("/{http_check_id}", response_model=schemas.HTTPCheck)
async def read_http_check(http_check_id: int, db: Session = Depends(get_db)):
    db_http_check = services.get_http_check(db, http_check_id=http_check_id)
    if db_http_check is None:
        return {"error": "HTTPCheck not found"}
    return db_http_check
