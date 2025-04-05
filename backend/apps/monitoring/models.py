# backend\apps\monitoring\models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class HTTPCheck(Base):
    """
    SQLAlchemy model for HTTP checks.
    """
    __tablename__ = "http_checks"

    id = Column(Integer, primary_key=True, index=True, comment="Unique identifier for the HTTP check")
    server = Column(String, comment="Target URL")
    method = Column(String, comment="Request method (GET, POST, etc.)")
    status_code = Column(Integer, comment="Response status code")
    result = Column(String, comment="Result of the operation")
    response_time = Column(Float, comment="Response time in seconds")
    content_length = Column(Integer, comment="Response body length in bytes")
    response_string_match = Column(Integer, comment="0 = mismatch / body read error, 1 = match")
    response_status_code_match = Column(Integer, comment="0 = mismatch, 1 = match")
    http_response_code = Column(Integer, comment="Response status code")
    result_type = Column(String, comment="Deprecated in 1.6: use `result` tag and `result_code` field")
    result_code = Column(Integer, comment="See below")
    time = Column(DateTime(timezone=True), server_default=func.now(), comment="Timestamp of the HTTP check")
