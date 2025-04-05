# backend\apps\monitoring\schemas.py
from pydantic import BaseModel
from datetime import datetime

class HTTPCheckBase(BaseModel):
    server: str
    method: str
    status_code: int
    result: str
    response_time: float
    content_length: int
    response_string_match: int
    response_status_code_match: int
    http_response_code: int
    result_type: str
    result_code: int

class HTTPCheckCreate(HTTPCheckBase):
    pass

class HTTPCheck(HTTPCheckBase):
    id: int
    time: datetime

    class Config:
        from_attributes = True
