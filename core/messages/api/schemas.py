from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class InputSendMessage(BaseModel):
    message: str
    folder: UUID


class InputGetMessages(BaseModel):
    folder: UUID


class OutputMessage(BaseModel):
    message: str
    created: datetime
    sender_name: str

    class Config:
        orm_mode = True
