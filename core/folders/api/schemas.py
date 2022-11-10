from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class InputFolderCreate(BaseModel):
    name: str
    parent: Optional[UUID]


class InputFolderDelete(BaseModel):
    id: UUID


class OutputFolder(BaseModel):
    name: str
    id: str


class OutputFolderTreeNode(BaseModel):
    folder: OutputFolder
    children: list["OutputFolderTreeNode"]


class OutputFolderTree(BaseModel):
    __root__: list[OutputFolderTreeNode]
