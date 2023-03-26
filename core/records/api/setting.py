from core.auth.models.org_user import RlcUser
from core.records.use_cases.setting import create_view
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.post()
def command__create_view(rlc_user: RlcUser, data: schemas.InputCreateView):
    create_view(rlc_user, data.name, data.columns)
   
