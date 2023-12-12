from core.auth.models import OrgUser
from core.questionnaires.use_cases.questionnaire import optimize_questionnaires
from core.seedwork.api_layer import Router

router = Router()


@router.post(url="optimize/")
def command__optimize(rlc_user: OrgUser):
    optimize_questionnaires(rlc_user)
