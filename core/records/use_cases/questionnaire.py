from core.auth.models import RlcUser
from core.records.models import Questionnaire, QuestionnaireTemplate, Record
from core.seedwork.use_case_layer import use_case
from core.static import PERMISSION_RECORDS_ADD_RECORD


@use_case(permissions=[PERMISSION_RECORDS_ADD_RECORD])
def publish_a_questionnaire(
    record: Record, template: QuestionnaireTemplate, __actor: RlcUser
):
    questionnaire = Questionnaire(record=record, template=template)
    questionnaire.save()
    return questionnaire
