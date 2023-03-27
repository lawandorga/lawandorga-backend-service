from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel


class InputAccess(BaseModel):
    uuid: UUID


class InputCreateAccess(BaseModel):
    record_uuid: UUID
    explanation: str = ""


class InputDeletion(BaseModel):
    uuid: UUID


class InputCreateDeletion(BaseModel):
    record_uuid: UUID
    explanation: str = ""


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
    uuid: UUID
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


class OutputDeletion(BaseModel):
    created: datetime
    explanation: str
    uuid: UUID
    processed_by_detail: str
    record_detail: str
    requested_by_detail: str
    state: str
    processed: Optional[datetime]

    class Config:
        orm_mode = True


class OutputAccessRequest(BaseModel):
    created: datetime
    uuid: UUID
    processed_by_detail: str
    requested_by_detail: str
    record_detail: str
    state: str
    processed_on: Optional[datetime]
    explanation: str

    class Config:
        orm_mode = True


class OutputRecordsPage(BaseModel):
    columns: list[str]
    records: list[OutputRecord]
    views: list[OutputView]
    deletions: list[OutputDeletion]
    access_requests: list[OutputAccessRequest]
