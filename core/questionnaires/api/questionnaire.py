from core.auth.models import RlcUser
from core.questionnaires.use_cases.questionnaire import optimize_questionnaires
from core.seedwork.api_layer import Router

router = Router()


@router.post(url="optimize/")
def command__optimize(rlc_user: RlcUser):
    optimize_questionnaires(rlc_user)
