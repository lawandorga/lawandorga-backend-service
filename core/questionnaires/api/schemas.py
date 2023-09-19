from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InputQuestionnaire(BaseModel):
    uuid: UUID


class InputPublishQuestionnaire(BaseModel):
    template: int
    folder: UUID


class OutputQuestionnaireTemplate(BaseModel):
    id: int
    name: str
    notes: str

    model_config = ConfigDict(from_attributes=True)


class OutputQuestionnaireField(BaseModel):
    id: int
    type: str
    name: str
    question: str

    model_config = ConfigDict(from_attributes=True)


class OutputQuestionnaireAnswer(BaseModel):
    id: int
    data: str
    field: OutputQuestionnaireField

    model_config = ConfigDict(from_attributes=True)


class OutputQuestionnaire(BaseModel):
    id: int
    uuid: UUID
    code: str
    template: OutputQuestionnaireTemplate
    answers: list[OutputQuestionnaireAnswer]
    created: datetime
    updated: datetime

    model_config = ConfigDict(from_attributes=True)
