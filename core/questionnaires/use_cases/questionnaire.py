from typing import Union
from uuid import UUID

from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import UploadedFile

from core.auth.models import OrgUser
from core.folders.usecases.finders import folder_from_uuid
from core.permissions.static import PERMISSION_RECORDS_ADD_RECORD
from core.questionnaires.models import Questionnaire
from core.questionnaires.models.questionnaire import QuestionnaireAnswer
from core.questionnaires.use_cases.finders import (
    questionnaire_from_id,
    questionnaire_from_id_dangerous,
    template_from_id,
)
from core.seedwork.use_case_layer import UseCaseError, use_case
from messagebus.domain.collector import EventCollector


@use_case(permissions=[PERMISSION_RECORDS_ADD_RECORD])
def publish_a_questionnaire(
    __actor: OrgUser,
    folder_uuid: UUID,
    template_id: int,
    collector: EventCollector,
):
    folder = folder_from_uuid(__actor, folder_uuid)
    template = template_from_id(__actor, template_id)
    questionnaire = Questionnaire.create(template, folder, __actor, collector)
    questionnaire.save()

    return questionnaire


@use_case
def delete_a_questionnaire(
    __actor: OrgUser, questionnaire_id: int, collector: EventCollector
):
    questionnaire = questionnaire_from_id(__actor, questionnaire_id)
    questionnaire.delete(collector)


@use_case
def submit_answers(
    __actor: AnonymousUser, questionnaire_id: int, **data: Union[UploadedFile, str]
):
    questionnaire = questionnaire_from_id_dangerous(__actor, questionnaire_id)
    for field in list(questionnaire.template.fields.all()):
        if field.name in data:
            answer = QuestionnaireAnswer(questionnaire=questionnaire, field=field)
            if field.type == "FILE":
                assert isinstance(data[field.name], UploadedFile)
                answer.upload_file(data[field.name])
            else:
                assert isinstance(data[field.name], str)
                if len(data[field.name]) > 190:
                    raise UseCaseError(
                        "The answer to the question '{}' can only be 190 characters long, because of encryption issues. "
                        "Your message is {} characters long.".format(
                            field.question, len(data[field.name])
                        )
                    )
                answer.data = data[field.name]  # type: ignore
            answer.encrypt()
            answer.save()


@use_case
def optimize_questionnaires(__actor: OrgUser):
    pass
