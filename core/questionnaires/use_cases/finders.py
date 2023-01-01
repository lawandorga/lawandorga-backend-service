from core.questionnaires.models import QuestionnaireTemplate


def questionnaire_template_from_id(actor, v) -> QuestionnaireTemplate:
    return QuestionnaireTemplate.objects.get(id=v, rlc__id=actor.org_id)
