from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InputFolderDetail(BaseModel):
    id: UUID


class OutputContent(BaseModel):
    uuid: UUID
    name: Optional[str]
    repository: str

    model_config = ConfigDict(from_attributes=True)


class OutputAvailableFolder(BaseModel):
    name: str
    id: UUID


class OutputFolder(BaseModel):
    name: str
    uuid: UUID
    stop_inherit: bool


class OutputAccess(BaseModel):
    name: str
    uuid: Optional[UUID]
    source: str
    actions: list[str]

    model_config = ConfigDict(from_attributes=True)


class OutputTreeFolder(BaseModel):
    name: str
    uuid: UUID
    stop_inherit: bool
    has_access: bool
    actions: dict[str, dict] = {}


class OutputFolderTreeNode(BaseModel):
    folder: OutputTreeFolder
    children: list["OutputFolderTreeNode"]
    content: list[OutputContent]
    access: list[OutputAccess]


class OutputSubfolder(BaseModel):
    name: str
    uuid: UUID

    model_config = ConfigDict(from_attributes=True)


class OutputFolderDetail(BaseModel):
    folder: OutputFolder
    access: list[OutputAccess]
    group_access: list[OutputAccess]
    content: list[OutputContent]
    subfolders: list[OutputSubfolder]
