from core.auth.models import RlcUser
from core.questionnaires.use_cases.questionnaire import publish_a_questionnaire
from core.records.api import schemas
from core.seedwork.api_layer import Router

router = Router()


@router.post(
    url="publish/",
    input_schema=schemas.InputPublishQuestionnaire,
    output_schema=schemas.OutputQuestionnaire,
)
def publish_questionnaire(data: schemas.InputPublishQuestionnaire, rlc_user: RlcUser):
    questionnaire = publish_a_questionnaire(
        rlc_user, record=data.record, template=data.template
    )
    return questionnaire
