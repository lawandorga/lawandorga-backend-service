from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OutputRlc(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class OutputEventResponse(BaseModel):
    id: int
    created: datetime
    updated: datetime
    is_global: bool
    name: str
    description: str
    start_time: datetime
    end_time: datetime
    org: OutputRlc

    class Config:
        orm_mode = True


class InputEventCreate(BaseModel):
    is_global: bool = False
    name: str
    description: str = ""
    start_time: datetime
    end_time: datetime


class InputEventUpdate(BaseModel):
    id: int
    is_global: Optional[bool]
    name: Optional[str]
    description: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]


class InputEventDelete(BaseModel):
    id: int
