from core.auth.models import RlcUser
from core.data_sheets.use_cases.access import (
    create_access_request,
    decline_access_request,
    grant_access_request,
)
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.post()
def command__create_access(rlc_user: RlcUser, data: schemas.InputCreateAccess):
    create_access_request(rlc_user, data.explanation, data.record)


@router.post(url="<int:id>/grant/")
def command__grant_access(rlc_user: RlcUser, data: schemas.InputAccess):
    grant_access_request(rlc_user, data.id)


@router.post(url="<int:id>/decline/")
def command__decline_access(rlc_user: RlcUser, data: schemas.InputAccess):
    decline_access_request(rlc_user, data.id)
