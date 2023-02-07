from core.auth.models import RlcUser
from core.seedwork.api_layer import Router

from ..models import Questionnaire
from . import schemas

router = Router()


@router.get(
    url="<uuid:uuid>/",
    output_schema=schemas.OutputQuestionnaire,
)
def query__retrieve_questionnaire(rlc_user: RlcUser, data: schemas.InputQuestionnaire):
    questionnaire: Questionnaire = (
        Questionnaire.objects.select_related("template")
        .prefetch_related("answers")
        .get(template__rlc_id=rlc_user.org_id, uuid=data.uuid)
    )
    answers = [
        answer.decrypt(user=rlc_user) for answer in list(questionnaire.answers.all())
    ]
    return {
        "id": questionnaire.id,
        "uuid": questionnaire.uuid,
        "code": questionnaire.code,
        "template": questionnaire.template,
        "answers": answers,
        "created": questionnaire.created,
        "updated": questionnaire.updated,
    }
