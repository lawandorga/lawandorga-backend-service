from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class InputTimelineList(BaseModel):
    folder_uuid: UUID


class InputTimelineEventCreate(BaseModel):
    folder_uuid: UUID
    title: str
    text: str
    time: datetime


class InputTimelineEventUpdate(BaseModel):
    title: str
    uuid: UUID
    folder_uuid: UUID
    text: str | None = None
    time: datetime | None = None


class InputTimelineEventDelete(BaseModel):
    folder_uuid: UUID
    uuid: UUID


class OutputTimelineEvent(BaseModel):
    uuid: UUID
    title: str
    text: str
    deleted: bool
    time: datetime

    class Config:
        orm_mode = True
