from core.auth.models import OrgUser
from core.records.use_cases.access import (
    create_access_request,
    decline_access_request,
    grant_access_request,
)
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.post()
def command__create_access(rlc_user: OrgUser, data: schemas.InputCreateAccess):
    create_access_request(rlc_user, data.explanation, data.record_uuid)


@router.post(url="<uuid:uuid>/grant/")
def command__grant_access(rlc_user: OrgUser, data: schemas.InputAccess):
    grant_access_request(rlc_user, data.uuid)


@router.post(url="<uuid:uuid>/decline/")
def command__decline_access(rlc_user: OrgUser, data: schemas.InputAccess):
    decline_access_request(rlc_user, data.uuid)
