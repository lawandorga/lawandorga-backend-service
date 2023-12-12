from core.auth.models import OrgUser
from core.records.use_cases.deletion import (
    accept_deletion_request,
    create_deletion_request,
    decline_deletion_request,
)
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.post()
def command__create_deletion(rlc_user: OrgUser, data: schemas.InputCreateDeletion):
    create_deletion_request(rlc_user, data.explanation, data.record_uuid)


@router.post(url="<uuid:uuid>/accept/")
def command__accept_deletion(rlc_user: OrgUser, data: schemas.InputDeletion):
    accept_deletion_request(rlc_user, data.uuid)


@router.post(url="<uuid:uuid>/decline/")
def command__decline_deletion(rlc_user: OrgUser, data: schemas.InputDeletion):
    decline_deletion_request(rlc_user, data.uuid)
