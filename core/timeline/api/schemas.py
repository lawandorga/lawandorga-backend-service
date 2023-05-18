from uuid import UUID

from pydantic import BaseModel


class InputTimelineList(BaseModel):
    folder_uuid: UUID


class InputTimelineEventCreate(BaseModel):
    folder_uuid: UUID
    text: str


class InputTimelineEventDelete(BaseModel):
    folder_uuid: UUID
    uuid: UUID


class OutputTimelineEvent(BaseModel):
    uuid: UUID
    text: str
    deleted: bool

    class Config:
        orm_mode = True
