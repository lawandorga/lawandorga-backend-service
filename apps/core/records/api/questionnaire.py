from apps.static.api_layer import PLACEHOLDER, Router
from apps.static.service_layer import ServiceResult

from ...auth.models import RlcUser
from ..use_cases.questionnaire import publish_a_questionnaire
from . import schemas

router = Router()


@router.post(
    url="publish/",
    input_schema=schemas.InputPublishQuestionnaire,
    output_schema=schemas.OutputQuestionnaire,
)
def publish_questionnaire(data: schemas.InputPublishQuestionnaire, rlc_user: RlcUser):
    questionnaire = publish_a_questionnaire(
        record=data.record, template=data.template, __actor=rlc_user
    )
    return ServiceResult(PLACEHOLDER, questionnaire)
