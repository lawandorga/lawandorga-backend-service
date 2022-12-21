from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class InputUploadFile(BaseModel):
    file: Any
    folder: UUID


class InputQueryFile(BaseModel):
    uuid: UUID


class InputDeleteFile(BaseModel):
    uuid: UUID


class OutputFile(BaseModel):
    uuid: UUID
    name: str
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True
