from uuid import UUID

from pydantic import BaseModel

from core.auth.models import RlcUser
from core.questionnaires.use_cases.questionnaire import (
    optimize_questionnaires,
    publish_a_questionnaire,
)
from core.seedwork.api_layer import Router


class InputPublishQuestionnaire(BaseModel):
    template: int
    folder: UUID


router = Router()


@router.post(
    url="publish/",
)
def publish_questionnaire(data: InputPublishQuestionnaire, rlc_user: RlcUser):
    publish_a_questionnaire(
        rlc_user, folder_uuid=data.folder, template_id=data.template
    )


@router.post(
    url="optimize/",
)
def command__optimize(rlc_user: RlcUser):
    optimize_questionnaires(rlc_user)
