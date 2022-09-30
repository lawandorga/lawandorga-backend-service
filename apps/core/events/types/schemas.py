from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Rlc(BaseModel):
    id: int
    name: str
    use_record_pool: bool

    class Config:
        orm_mode = True


class EventResponse(BaseModel):
    id: int
    created: datetime
    updated: datetime
    is_global: bool
    name: str
    description: str
    start_time: datetime
    end_time: datetime
    org: Rlc

    class Config:
        orm_mode = True


class EventCreate(BaseModel):
    is_global: bool
    name: str
    description: str
    start_time: datetime
    end_time: datetime


class EventUpdate(BaseModel):
    id: int
    is_global: Optional[bool]
    name: Optional[str]
    description: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
