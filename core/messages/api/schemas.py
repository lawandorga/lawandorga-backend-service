from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InputSendMessage(BaseModel):
    message: str
    folder: UUID


class InputGetMessages(BaseModel):
    folder: UUID


class OutputMessage(BaseModel):
    message: str
    created: datetime
    sender_name: str

    model_config = ConfigDict(from_attributes=True)
