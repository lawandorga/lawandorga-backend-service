from typing import Literal

from django.core.files.uploadedfile import UploadedFile

from core.auth.models.org_user import RlcUser
from core.permissions.static import PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES
from core.questionnaires.models.template import QuestionnaireTemplate
from core.questionnaires.use_cases.finders import (
    template_file_from_id,
    template_from_id,
    template_question_from_id,
)
from core.seedwork.use_case_layer import use_case


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES])
def create_questionnaire_template(__actor: RlcUser, name: str, notes: str):
    template = QuestionnaireTemplate.create(name=name, org=__actor.org, notes=notes)
    template.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES])
def update_questionnaire_template(
    __actor: RlcUser, template_id: int, name: str, notes: str
):
    template = template_from_id(__actor, template_id)
    template.update(name=name, notes=notes)
    template.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES])
def delete_questionnaire_template(__actor: RlcUser, template_id: int):
    template = template_from_id(__actor, template_id)
    template.delete()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES])
def create_question(
    __actor: RlcUser,
    template_id: int,
    field_type: Literal["TEXTAREA", "FILE"],
    question: str,
    order: int,
):
    template = template_from_id(__actor, template_id)
    q = template.add_question(field_type, question, order)
    q.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES])
def update_question(
    __actor: RlcUser,
    question_id: int,
    field_type: Literal["TEXTAREA", "FILE"],
    question: str,
    order: int,
):
    field = template_question_from_id(__actor, question_id)
    field.update(field_type, question, order)
    field.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES])
def delete_question(__actor: RlcUser, question_id: int):
    field = template_question_from_id(__actor, question_id)
    field.delete()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES])
def add_file(__actor: RlcUser, template_id: int, name: str, file: UploadedFile):
    template = template_from_id(__actor, template_id)
    template.add_file(name, file)


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES])
def delete_file(__actor: RlcUser, file_id: int):
    file = template_file_from_id(__actor, file_id)
    file.file.delete()
    file.delete()
