from datetime import datetime

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
