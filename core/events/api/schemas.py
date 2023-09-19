import uuid
from datetime import datetime
from typing import Literal, Optional

from django.utils.timezone import localtime
from pydantic import BaseModel, ConfigDict, field_validator


class OutputRlc(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


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
    level: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("start_time", "end_time")
    def format_datetime_validator(cls, v: datetime) -> datetime:
        v = localtime(v)
        return v


class InputEventCreate(BaseModel):
    name: str
    description: str = ""
    level: Literal["ORG", "META", "GLOBAL"]
    start_time: datetime
    end_time: datetime

    # _ = make_datetime_aware("start_time")
    # __ = make_datetime_aware("end_time")


class InputEventUpdate(BaseModel):
    id: int
    is_global: Optional[bool] = None
    name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    # _ = make_datetime_aware("start_time")
    # __ = make_datetime_aware("end_time")


class InputEventDelete(BaseModel):
    id: int


class CalendarUuidUser(BaseModel):
    id: int
    calendar_uuid: uuid.UUID
    calendar_url: str
