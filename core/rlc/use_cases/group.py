from core.auth.models import RlcUser
from core.auth.use_cases.finders import rlc_user_from_id
from core.rlc.use_cases.finders import group_from_id
from core.seedwork.use_case_layer import UseCaseError, use_case
from core.static import PERMISSION_ADMIN_MANAGE_GROUPS


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_GROUPS])
def add_member_to_group(__actor: RlcUser, group_id: int, new_member_id: int):
    group = group_from_id(__actor, group_id)
    new_member = rlc_user_from_id(__actor, new_member_id)

    if group.from_rlc_id != new_member.org_id:
        raise UseCaseError("You can not edit a member from another org.")

    group.add_member(new_member)


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_GROUPS])
def remove_member_from_group(__actor: RlcUser, group_id: int, member_id: int):
    group = group_from_id(__actor, group_id)
    member = rlc_user_from_id(__actor, member_id)

    if group.from_rlc_id != member.org_id:
        raise UseCaseError("You can not edit a member from another org.")

    group.remove_member(member)
