from datetime import datetime
from typing import Optional

from django.utils.timezone import localtime
from pydantic import BaseModel, validator

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


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

    @validator("start_time")
    def localtime_1(cls, v: datetime):
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            return v.strftime(DATETIME_FORMAT)
        return localtime(v).strftime(DATETIME_FORMAT)

    @validator("end_time")
    def localtime_2(cls, v):
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            return v.strftime(DATETIME_FORMAT)
        return localtime(v).strftime(DATETIME_FORMAT)


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
