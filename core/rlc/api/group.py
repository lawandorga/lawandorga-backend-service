from typing import List

from core.auth.models import RlcUser
from core.rlc.api import schemas
from core.rlc.models import Group
from core.rlc.use_cases.group import add_member_to_group, remove_member_from_group
from core.seedwork.api_layer import Router

router = Router()


# list
@router.get(
    url="<int:id>/users/",
    input_schema=schemas.InputListUsersGet,
    output_schema=List[schemas.OutputGroupMember],
)
def list_users(data: schemas.InputListUsersGet, rlc_user: RlcUser):
    group = Group.objects.get(from_rlc=rlc_user.org, id=data.id)

    users = group.members.all()
    users_list = list(users)

    return users_list


# add member
@router.post(url="<int:id>/add_member/", input_schema=schemas.InputAddMember)
def add_member(data: schemas.InputAddMember, rlc_user: RlcUser):
    add_member_to_group(data.id, data.new_member, __actor=rlc_user)


# remove member
@router.post(url="<int:id>/remove_member/", input_schema=schemas.InputRemoveMember)
def remove_member(data: schemas.InputRemoveMember, rlc_user: RlcUser):
    remove_member_from_group(data.id, data.member, __actor=rlc_user)
