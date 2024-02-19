from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InputAccess(BaseModel):
    uuid: UUID


class InputCreateAccess(BaseModel):
    record_uuid: UUID
    explanation: str = ""


class InputCreateView(BaseModel):
    name: str
    columns: list[str]
    shared: bool = False


class InputUpdateView(BaseModel):
    uuid: UUID
    name: str
    columns: list[str]
    ordering: int


class InputDeleteView(BaseModel):
    uuid: UUID


class InputCreateRecord(BaseModel):
    token: str
    template: Optional[int] = None


class InputChangeRecordToken(BaseModel):
    uuid: UUID
    token: str


class OutputCreateRecord(BaseModel):
    folder_uuid: UUID
    record_uuid: UUID | None = None


class OutputRecord(BaseModel):
    uuid: UUID
    token: str
    attributes: dict[str, Union[str, list[str]]]
    delete_requested: bool
    has_access: bool
    folder_uuid: UUID
    data_sheet_uuid: Optional[UUID]

    model_config = ConfigDict(from_attributes=True)


class OutputView(BaseModel):
    name: str
    columns: list[str]
    uuid: UUID
    shared: bool
    ordering: int

    model_config = ConfigDict(from_attributes=True)


class OutputDeletion(BaseModel):
    created: datetime
    explanation: str
    uuid: UUID
    processed_by_detail: str
    record_detail: str
    requested_by_detail: str
    state: str
    processed: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class OutputAccessRequest(BaseModel):
    created: datetime
    uuid: UUID
    processed_by_detail: str
    requested_by_detail: str
    record_detail: str
    state: str
    processed_on: Optional[datetime]
    explanation: str

    model_config = ConfigDict(from_attributes=True)


class OutputBadges(BaseModel):
    deletion_requests: int
    access_requests: int


class OutputRecordsPage(BaseModel):
    records: list[OutputRecord]
    views: list[OutputView]
    deletions: list[OutputDeletion]
    access_requests: list[OutputAccessRequest]
    badges: OutputBadges
