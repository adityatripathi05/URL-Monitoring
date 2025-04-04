# backend\apps\monitoring\models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class HTTPCheck(Base):
    __tablename__ = "http_checks"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    status_code = Column(Integer)
    response_time = Column(Float)
    success = Column(Boolean)
    time = Column(DateTime(timezone=True), server_default=func.now())
