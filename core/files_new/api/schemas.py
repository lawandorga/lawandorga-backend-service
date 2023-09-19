from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InputUploadMultipleFiles(BaseModel):
    files: Any
    folder: UUID


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

    model_config = ConfigDict(from_attributes=True)
