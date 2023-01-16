from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from core.seedwork.api_layer import qs_to_list


class InputCreateLink(BaseModel):
    name: str
    folder: UUID


class InputUploadFile(BaseModel):
    name: str
    link: UUID
    file: Any


class InputDeleteLink(BaseModel):
    link: UUID


class InputDisableLink(BaseModel):
    link: UUID


class InputQueryLink(BaseModel):
    uuid: UUID


class InputDownloadFile(BaseModel):
    file: UUID
    link: UUID


class OutputUploadFile(BaseModel):
    name: str
    uuid: UUID
    created: datetime

    class Config:
        orm_mode = True


class OutputQueryLink(BaseModel):
    uuid: UUID
    name: str
    link: str
    created: datetime
    disabled: bool
    files: list[OutputUploadFile]

    class Config:
        orm_mode = True

    _ = qs_to_list("files")
