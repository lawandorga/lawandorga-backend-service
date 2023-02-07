from core.auth.models import RlcUser
from core.records.use_cases.templates import (
    create_template,
    delete_template,
    update_template,
)
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.post()
def command__create_template(rlc_user: RlcUser, data: schemas.InputTemplateCreate):
    create_template(rlc_user, data.name)


@router.put(url="<int:id>/")
def command__update_template(rlc_user: RlcUser, data: schemas.InputTemplateUpdate):
    update_template(rlc_user, data.id, data.name, data.show)


@router.delete(url="<int:id>/")
def command__delete_template(rlc_user: RlcUser, data: schemas.InputTemplateDelete):
    delete_template(rlc_user, data.id)
