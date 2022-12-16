from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from core.seedwork.api_layer import qs_to_list


class InputFolderDetail(BaseModel):
    id: UUID


class InputFolderCreate(BaseModel):
    name: str
    parent: Optional[UUID]


class InputFolderUpdate(BaseModel):
    name: str
    id: UUID


class InputFolderAccess(BaseModel):
    user_uuid: UUID
    id: UUID


class InputFolderDelete(BaseModel):
    id: UUID


class OutputContent(BaseModel):
    name: Optional[str]
    actions: dict[str, str]

    class Config:
        orm_mode = True


class OutputAvailableFolder(BaseModel):
    name: str
    id: UUID


class OutputFolder(BaseModel):
    name: str
    id: str


class OutputAccess(BaseModel):
    name: str
    uuid: Optional[UUID]

    class Config:
        orm_mode = True


class OutputFolderTreeNode(BaseModel):
    folder: OutputFolder
    children: list["OutputFolderTreeNode"]
    content: list[OutputContent]
    access: list[OutputAccess]


class OutputFolderPage(BaseModel):
    tree: list[OutputFolderTreeNode]
    available_persons: list[OutputAccess]

    _ = qs_to_list("available_persons")


class OutputFolderDetail(BaseModel):
    folder: OutputFolder
    access: list[OutputAccess]
