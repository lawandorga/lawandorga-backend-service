from core.auth.models import RlcUser
from core.records.use_cases.deletion import (
    accept_deletion_request,
    decline_deletion_request, create_deletion_request,
)
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.post(input_schema=schemas.InputCreateDeletion)
def command__create_deletion(rlc_user: RlcUser, data: schemas.InputCreateDeletion):
    create_deletion_request(rlc_user, data.explanation, data.record)


@router.post(url='<int:id>/accept/', input_schema=schemas.InputDeletion)
def command__accept_deletion(rlc_user: RlcUser, data: schemas.InputDeletion):
    accept_deletion_request(rlc_user, data.id)


@router.post(url='<int:id>/decline/', input_schema=schemas.InputDeletion)
def command__decline_deletion(rlc_user: RlcUser, data: schemas.InputDeletion):
    decline_deletion_request(rlc_user, data.id)
