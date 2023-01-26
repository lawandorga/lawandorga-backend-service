from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel


class InputQueryRecord(BaseModel):
    uuid: UUID


class InputRecordCreate(BaseModel):
    name: str
    template: int


class InputRecordCreateWithinFolder(BaseModel):
    name: str
    template: int
    folder: UUID


class InputAccess(BaseModel):
    id: int


class InputCreateAccess(BaseModel):
    record: int
    explanation: str


class InputRecordChangeName(BaseModel):
    id: int
    name: str


class InputDeletion(BaseModel):
    id: int


class InputCreateDeletion(BaseModel):
    record: int
    explanation: str


class OutputRecordDeletion(BaseModel):
    created: datetime
    explanation: str
    id: int
    processed_by_detail: str
    record_detail: str
    requested_by_detail: str
    state: str
    processed: Optional[datetime]

    class Config:
        orm_mode = True


class OutputRecordAccess(BaseModel):
    created: datetime
    id: int
    processed_by_detail: str
    requested_by_detail: str
    record_detail: str
    state: str
    processed_on: Optional[datetime]
    explanation: str

    class Config:
        orm_mode = True


class OutputRecordCreate(BaseModel):
    id: int
    folder_uuid: UUID
    uuid: UUID


class OutputEntry(BaseModel):
    value: str

    class Config:
        orm_mode = True


class OutputOption(BaseModel):
    name: str
    id: int


class OutputField(BaseModel):
    id: int
    entry_url: str
    kind: str
    label: str
    name: str
    options: Optional[list[OutputOption | str]]
    type: str


class OutputDetailEntry(BaseModel):
    name: str
    type: str
    url: str
    value: str | int | list[int] | list[str]


class OutputClient(BaseModel):
    name: str
    phone_number: str
    note: str

    class Config:
        orm_mode = True


class OutputRecordDetail(BaseModel):
    created: datetime
    updated: datetime
    id: int
    uuid: UUID
    folder_uuid: UUID
    name: str
    client: Optional[OutputClient]
    fields: list[OutputField]
    entries: dict[str, OutputDetailEntry]


class OutputRecord(BaseModel):
    id: int
    uuid: UUID
    attributes: dict[str, Union[str, list[str]]]
    delete_requested: bool
    has_access: bool
    folder_uuid: Optional[UUID]

    class Config:
        orm_mode = True


class OutputRecordsPage(BaseModel):
    columns: list[str]
    records: list[OutputRecord]
