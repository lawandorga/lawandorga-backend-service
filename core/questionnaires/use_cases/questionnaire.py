from typing import Union
from uuid import UUID

from django.core.files.uploadedfile import UploadedFile

from core.auth.models import RlcUser
from core.folders.use_cases.finders import folder_from_uuid
from core.permissions.static import PERMISSION_RECORDS_ADD_RECORD
from core.questionnaires.models import Questionnaire
from core.questionnaires.models.questionnaire import QuestionnaireAnswer
from core.questionnaires.use_cases.finders import (
    questionnaire_from_id,
    template_from_id,
)
from core.seedwork.use_case_layer import UseCaseError, use_case


@use_case(permissions=[PERMISSION_RECORDS_ADD_RECORD])
def publish_a_questionnaire(
    __actor: RlcUser,
    folder_uuid: UUID,
    template_id: int,
):
    folder = folder_from_uuid(__actor, folder_uuid)
    template = template_from_id(__actor, template_id)
    questionnaire = Questionnaire.create(template, folder, __actor)
    questionnaire.save()

    return questionnaire


@use_case
def delete_a_questionnaire(__actor: RlcUser, questionnaire_id: int):
    questionnaire = questionnaire_from_id(__actor, questionnaire_id)
    questionnaire.delete()


@use_case
def submit_answers(
    __actor: RlcUser, questionnaire_id: int, **data: Union[UploadedFile, str]
):
    questionnaire = questionnaire_from_id(__actor, questionnaire_id)
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
def optimize_questionnaires(__actor: RlcUser):
    qs_1 = Questionnaire.objects.filter(template__rlc_id=__actor.org_id)
    qs_2: list[Questionnaire] = list(qs_1)
    for q in qs_2:
        if q.folder_uuid is None:
            q.put_in_folder(__actor)
