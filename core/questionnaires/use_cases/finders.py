from core.questionnaires.models import QuestionnaireTemplate
from core.seedwork.use_case_layer import finder_function


@finder_function
def questionnaire_template_from_id(actor, v) -> QuestionnaireTemplate:
    return QuestionnaireTemplate.objects.get(id=v, rlc__id=actor.org_id)
