from typing import List

from apps.core.auth.models import RlcUser
from apps.static.api_layer import Router
from apps.static.service_layer import ServiceResult

from ..models import ExternalLink, Group
from . import schemas

router = Router()

# list
LIST_USERS_SUCCESS = "User {} has successfully retrieved all external links."
LIST_USERS_ERROR = 'User {} tried to get users from a group that could not be found.'


@router.get(url="<int:id>/users/", input_schema=schemas.ListUsersGetInput, output_schema=List[schemas.GroupMember])
def list_users(data: schemas.ListUsersGetInput, rlc_user: RlcUser):
    group = Group.objects.filter(from_rlc=rlc_user.org, id=data.id).first()
    if group is None:
        return ServiceResult(LIST_USERS_ERROR, error='The group could not be found')
    users_list = list(map(lambda x: x.rlc_user, list(group.group_members.select_related('rlc_user'))))
    return ServiceResult(LIST_USERS_SUCCESS, users_list)
