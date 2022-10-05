from typing import List

from apps.core.auth.models import RlcUser
from apps.static.api_layer import PLACEHOLDER, Router
from apps.static.service_layer import ServiceResult

from ..models import Group
from ..use_cases.group import add_member_to_group, remove_member_from_group
from . import schemas

router = Router()

# list
LIST_USERS_SUCCESS = "User {} has successfully retrieved all external links."
LIST_USERS_ERROR = "User {} tried to get users from a group that could not be found."


@router.get(
    url="<int:id>/users/",
    input_schema=schemas.ListUsersGetInput,
    output_schema=List[schemas.GroupMember],
)
def list_users(data: schemas.ListUsersGetInput, rlc_user: RlcUser):
    group = Group.objects.get(from_rlc=rlc_user.org, id=data.id)

    users = group.members.all()
    users_list = list(users)

    return ServiceResult(LIST_USERS_SUCCESS, users_list)


# add member
@router.post(url="<int:id>/add_member/", input_schema=schemas.InputAddMember)
def add_member(data: schemas.InputAddMember, rlc_user: RlcUser):
    add_member_to_group(data.id, data.new_member, __actor=rlc_user)
    return ServiceResult(PLACEHOLDER)


# remove member
@router.post(url="<int:id>/remove_member/", input_schema=schemas.InputRemoveMember)
def remove_member(data: schemas.InputRemoveMember, rlc_user: RlcUser):
    remove_member_from_group(data.id, data.member, __actor=rlc_user)
    return ServiceResult(PLACEHOLDER)
