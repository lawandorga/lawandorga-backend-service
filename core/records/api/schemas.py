from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from core.seedwork.api_layer import qs_to_list


class InputPublishQuestionnaire(BaseModel):
    template: int
    record: int


class InputRecordCreate(BaseModel):
    name: str
    template: int
    folder: Optional[UUID]


class InputRecordChangeName(BaseModel):
    id: int
    name: str


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


class OutputRecord(BaseModel):
    id: int
    attributes: dict[str, Union[str, list[str]]]
    delete_requested: bool
    has_access: bool

    class Config:
        orm_mode = True


class OutputRecordsPage(BaseModel):
    columns: list[str]
    records: list[OutputRecord]
