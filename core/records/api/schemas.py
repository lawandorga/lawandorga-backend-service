from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel


class InputCreateView(BaseModel):
    name: str
    columns: list[str]


class InputUpdateView(BaseModel):
    uuid: UUID
    name: str
    columns: list[str]


class InputDeleteView(BaseModel):
    uuid: UUID


class InputCreateRecord(BaseModel):
    token: str
    template: Optional[int]


class InputChangeRecordToken(BaseModel):
    uuid: UUID
    token: str


class OutputCreateRecord(BaseModel):
    folder_uuid: UUID


class OutputRecord(BaseModel):
    token: str
    attributes: dict[str, Union[str, list[str]]]
    delete_requested: bool
    has_access: bool
    folder_uuid: UUID
    data_sheet_uuid: Optional[UUID]

    class Config:
        orm_mode = True


class OutputView(BaseModel):
    name: str
    columns: list[str]
    uuid: UUID

    class Config:
        orm_mode = True


class OutputRecordsPage(BaseModel):
    columns: list[str]
    records: list[OutputRecord]
    views: list[OutputView]
