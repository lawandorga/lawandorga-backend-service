from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from core.seedwork.api_layer import qs_to_list


class InputPublishQuestionnaire(BaseModel):
    template: int
    record: int


class InputQueryRecord(BaseModel):
    uuid: UUID


class InputRecordCreate(BaseModel):
    name: str
    template: int
    folder: Optional[UUID]


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


class OutputRecordCreate(BaseModel):
    id: int


class OutputQuestionnaireTemplate(BaseModel):
    id: int
    name: str
    notes: str

    class Config:
        orm_mode = True


class OutputQuestionnaireField(BaseModel):
    id: int
    type: str
    name: str
    question: str

    class Config:
        orm_mode = True


class OutputQuestionnaireAnswer(BaseModel):
    id: int
    data: str
    field: OutputQuestionnaireField

    class Config:
        orm_mode = True


class OutputQuestionnaire(BaseModel):
    id: int
    code: str
    template: OutputQuestionnaireTemplate
    answers: List[OutputQuestionnaireAnswer]
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True

    _ = qs_to_list("answers")


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
