# backend\apps\monitoring\schemas.py
from pydantic import BaseModel
from datetime import datetime

class HTTPCheckBase(BaseModel):
    url: str
    status_code: int
    response_time: float
    success: bool

class HTTPCheckCreate(HTTPCheckBase):
    pass

class HTTPCheck(HTTPCheckBase):
    id: int
    time: datetime

    class Config:
        orm_mode = True
