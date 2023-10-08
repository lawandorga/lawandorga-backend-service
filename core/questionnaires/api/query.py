import mimetypes
from datetime import datetime
from uuid import UUID

from django.http import FileResponse
from pydantic import BaseModel, ConfigDict

from core.auth.models import RlcUser
from core.questionnaires.models import Questionnaire
from core.questionnaires.models.template import (
    QuestionnaireTemplate,
    QuestionnaireTemplateFile,
)
from core.seedwork.api_layer import Router

router = Router()


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


class InputQuestionnaire(BaseModel):
    uuid: UUID


@router.get(
    url="<uuid:uuid>/",
    output_schema=OutputQuestionnaire,
)
def query__retrieve_questionnaire(rlc_user: RlcUser, data: InputQuestionnaire):
    questionnaire = (
        Questionnaire.objects.select_related("template")
        .prefetch_related("answers")
        .get(template__rlc_id=rlc_user.org_id, uuid=data.uuid)
    )
    answers = [
        answer.decrypt(user=rlc_user) for answer in list(questionnaire.answers.all())
    ]
    return {
        "id": questionnaire.pk,
        "uuid": questionnaire.uuid,
        "code": questionnaire.code,
        "template": questionnaire.template,
        "answers": answers,
        "created": questionnaire.created,
        "updated": questionnaire.updated,
    }


class OutputTemplateList(BaseModel):
    id: int
    name: str
    notes: str

    model_config = ConfigDict(from_attributes=True)


@router.get("templates/", output_schema=list[OutputTemplateList])
def query__list_templates(rlc_user: RlcUser):
    return QuestionnaireTemplate.objects.filter(rlc=rlc_user.org)


class OutputTemplateDetailField(BaseModel):
    id: int
    name: str
    order: int
    question: str
    type: str

    model_config = ConfigDict(from_attributes=True)


class OutputTemplateDetailFile(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class OutputTemplateDetail(BaseModel):
    id: int
    name: str
    notes: str
    fields: list[OutputTemplateDetailField]
    files: list[OutputTemplateDetailFile]

    model_config = ConfigDict(from_attributes=True)


class InputRetrieveTemplate(BaseModel):
    id: int


@router.get("template/<int:id>/", output_schema=OutputTemplateDetail)
def query__retrieve_template(rlc_user: RlcUser, data: InputRetrieveTemplate):
    template = QuestionnaireTemplate.objects.filter(rlc=rlc_user.org).get(id=data.id)
    return {
        "id": template.pk,
        "name": template.name,
        "notes": template.notes,
        "fields": list(template.fields.all()),
        "files": list(template.files.all()),
    }


class InputDownloadFile(BaseModel):
    id: int


@router.get("download_template_file/<int:id>/", output_schema=FileResponse)
def query__retrieve_file(rlc_user: RlcUser, data: InputDownloadFile):
    file = QuestionnaireTemplateFile.objects.get(
        id=data.id, questionnaire__rlc__id=rlc_user.org_id
    )
    response = FileResponse(
        file.file, content_type=mimetypes.guess_type(file.file.name)[0]
    )
    response["Content-Disposition"] = 'attachment; filename="{}"'.format(file.name)
    return response
