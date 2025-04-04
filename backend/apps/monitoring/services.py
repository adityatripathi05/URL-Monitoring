# backend\apps\monitoring\services.py
from sqlalchemy.orm import Session
from . import models, schemas

def get_http_check(db: Session, http_check_id: int):
    return db.query(models.HTTPCheck).filter(models.HTTPCheck.id == http_check_id).first()

def get_http_checks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.HTTPCheck).offset(skip).limit(limit).all()

def create_http_check(db: Session, http_check: schemas.HTTPCheckCreate):
    db_http_check = models.HTTPCheck(**http_check.dict())
    db.add(db_http_check)
    db.commit()
    db.refresh(db_http_check)
    return db_http_check
