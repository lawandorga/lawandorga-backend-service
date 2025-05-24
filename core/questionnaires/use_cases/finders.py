from core.auth.models.org_user import OrgUser
from core.questionnaires.models import QuestionnaireTemplate
from core.questionnaires.models.questionnaire import Questionnaire
from core.questionnaires.models.template import (
    QuestionnaireQuestion,
    QuestionnaireTemplateFile,
)
from core.seedwork.use_case_layer import finder_function
from django.contrib.auth.models import AnonymousUser

@finder_function
def template_from_id(actor: OrgUser, v: int) -> QuestionnaireTemplate:
    return QuestionnaireTemplate.objects.get(id=v, org__id=actor.org_id)


@finder_function
def template_question_from_id(actor: OrgUser, v: int) -> QuestionnaireQuestion:
    return QuestionnaireQuestion.objects.get(id=v, questionnaire__org__id=actor.org_id)


@finder_function
def template_file_from_id(actor: OrgUser, v: int) -> QuestionnaireTemplateFile:
    return QuestionnaireTemplateFile.objects.get(
        id=v, questionnaire__org__id=actor.org_id
    )


@finder_function
def questionnaire_from_id(actor: OrgUser, v: int) -> Questionnaire:
    return Questionnaire.objects.get(id=v, template__org__id=actor.org_id)


@finder_function
def questionnaire_from_id_dangerous(_: AnonymousUser, v: int) -> Questionnaire:
    return Questionnaire.objects.get(id=v)
