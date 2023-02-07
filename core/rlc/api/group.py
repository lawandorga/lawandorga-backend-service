from core.auth.models import RlcUser
from core.rlc.use_cases.group import (
    add_member_to_group,
    create_group,
    delete_group,
    remove_member_from_group,
    update_group,
)
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.post()
def command__create_group(rlc_user: RlcUser, data: schemas.InputGroupCreate):
    create_group(rlc_user, data.name, data.description)


@router.put(url="<int:id>/")
def command__update_group(rlc_user: RlcUser, data: schemas.InputGroupUpdate):
    update_group(rlc_user, data.id, data.name, data.description)


@router.delete(url="<int:id>/")
def command__delete_group(rlc_user: RlcUser, data: schemas.InputGroupDelete):
    delete_group(rlc_user, data.id)


@router.post(url="<int:id>/add_member/")
def command__add_member(data: schemas.InputAddMember, rlc_user: RlcUser):
    add_member_to_group(rlc_user, data.id, data.new_member)


@router.post(url="<int:id>/remove_member/")
def command__remove_member(data: schemas.InputRemoveMember, rlc_user: RlcUser):
    remove_member_from_group(rlc_user, data.id, data.member)
