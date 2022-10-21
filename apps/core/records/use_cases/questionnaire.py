from apps.core.auth.models import RlcUser
from apps.core.records.models import Questionnaire, QuestionnaireTemplate, Record
from apps.core.static import PERMISSION_RECORDS_ADD_RECORD
from apps.core.seedwork.use_case_layer import use_case


@use_case(permissions=[PERMISSION_RECORDS_ADD_RECORD])
def publish_a_questionnaire(
    record: Record, template: QuestionnaireTemplate, __actor: RlcUser
):
    questionnaire = Questionnaire(record=record, template=template)
    questionnaire.save()
    return questionnaire
