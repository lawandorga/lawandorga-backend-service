from datetime import datetime
from typing import List

from pydantic import BaseModel

from apps.static.api_layer import qs_to_list


class InputPublishQuestionnaire(BaseModel):
    template: int
    record: int


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
