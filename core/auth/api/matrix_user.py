from core.auth.models import OrgUser
from core.auth.use_cases.matrix_user import create_matrix_user
from core.seedwork.api_layer import Router

router = Router()


@router.post()
def command__create_matrix_user(rlc_user: OrgUser):
    create_matrix_user(rlc_user)
