from core.auth.models import RlcUser
from core.auth.use_cases.matrix_user import create_matrix_user
from core.seedwork.api_layer import Router

router = Router()


@router.post()
def command__create_matrix_user(rlc_user: RlcUser):
    create_matrix_user(rlc_user)
