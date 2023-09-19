from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)


class OutputQueryLink(BaseModel):
    uuid: UUID
    name: str
    link: str
    created: datetime
    disabled: bool
    files: list[OutputUploadFile]

    model_config = ConfigDict(from_attributes=True)


class OutputQueryLinkPublic(BaseModel):
    uuid: UUID
    name: str
    link: str
    created: datetime
    disabled: bool

    model_config = ConfigDict(from_attributes=True)
