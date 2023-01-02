from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from core.seedwork.api_layer import qs_to_list


class InputQuestionnaire(BaseModel):
    uuid: UUID


class InputPublishQuestionnaire(BaseModel):
    template: int
    folder: UUID


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
    uuid: UUID
    code: str
    template: OutputQuestionnaireTemplate
    answers: list[OutputQuestionnaireAnswer]
    created: datetime
    updated: datetime

    class Config:
        orm_mode = True

    _ = qs_to_list("answers")
