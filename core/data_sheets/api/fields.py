from core.auth.models import RlcUser
from core.data_sheets.use_cases.field import delete_field
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.delete("<uuid:uuid>/")
def command__delete_field(rlc_user: RlcUser, data: schemas.InputFieldDelete):
    delete_field(rlc_user, data.uuid, data.force_delete)
