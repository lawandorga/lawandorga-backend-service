from typing import Any
from uuid import UUID

from pydantic import BaseModel


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
    item: UUID


class InputDownloadFile(BaseModel):
    file: UUID
    link: UUID


class OutputQueryLink(BaseModel):
    uuid: UUID
