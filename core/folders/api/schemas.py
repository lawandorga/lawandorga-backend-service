from typing import Optional

from pydantic import BaseModel


class InputFolderCreate(BaseModel):
    name: str
    parent: Optional[str]


class OutputFolder(BaseModel):
    name: str
    id: str


class OutputFolderDeep(BaseModel):
    __root__: tuple[OutputFolder, list["OutputFolderDeep"]]


class OutputFolderTree(BaseModel):
    __root__: list[tuple[OutputFolder, list[OutputFolderDeep]]]
