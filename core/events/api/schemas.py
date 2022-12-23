import uuid
from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel

from core.events.models import Attendance
from core.seedwork.api_layer import format_datetime, make_datetime_aware


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

    _ = format_datetime("start_time")
    __ = format_datetime("end_time")


class InputEventCreate(BaseModel):
    is_global: bool = False
    name: str
    description: str = ""
    start_time: datetime
    end_time: datetime

    _ = make_datetime_aware("start_time")
    __ = make_datetime_aware("end_time")


class InputEventUpdate(BaseModel):
    id: int
    is_global: Optional[bool]
    name: Optional[str]
    description: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]

    _ = make_datetime_aware("start_time")
    __ = make_datetime_aware("end_time")


class InputEventDelete(BaseModel):
    id: int


class CalendarUuidUser(BaseModel):
    id: int
    calendar_uuid: uuid.UUID
    calendar_url: str


class InputAttendanceUpdate(BaseModel):
    status: Literal[Attendance.ATTENDING, Attendance.UNSURE, Attendance.ABSENT]
    id: int


class InputAttendanceCreate(BaseModel):
    event_id: int
    status: Literal[Attendance.ATTENDING, Attendance.UNSURE, Attendance.ABSENT]


class InputAttendanceDelete(BaseModel):
    id: int


class OutputRLCUser(BaseModel):
    name: str
    email: str

    class Config:
        orm_mode = True


class OutputAttendanceResponse(BaseModel):
    event: OutputEventResponse
    rlc_user: OutputRLCUser
    status: str
    id: int

    class Config:
        orm_mode = True
