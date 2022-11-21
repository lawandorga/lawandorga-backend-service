from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class InputFolderCreate(BaseModel):
    name: str
    parent: Optional[UUID]


class InputFolderUpdate(BaseModel):
    name: str
    id: UUID


class InputFolderDelete(BaseModel):
    id: UUID


class OutputContent(BaseModel):
    name: str

    class Config:
        orm_mode = True


class OutputFolder(BaseModel):
    name: str
    id: str


class OutputFolderTreeNode(BaseModel):
    folder: OutputFolder
    children: list["OutputFolderTreeNode"]
    content: list[OutputContent]
    access: list[str]


class OutputFolderTree(BaseModel):
    __root__: list[OutputFolderTreeNode]
