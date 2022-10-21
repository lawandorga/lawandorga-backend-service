from apps.core.auth.models import RlcUser
from apps.core.rlc.models import Group
from apps.core.static import PERMISSION_ADMIN_MANAGE_GROUPS
from apps.seedwork.use_case_layer import UseCaseError, use_case


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_GROUPS])
def add_member_to_group(group: Group, new_member: RlcUser, __actor: RlcUser):
    if group.from_rlc_id != new_member.org_id:
        raise UseCaseError("You can not edit a member from another org.")

    group.add_member(new_member)


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_GROUPS])
def remove_member_from_group(group: Group, member: RlcUser, __actor: RlcUser):
    if group.from_rlc_id != member.org_id:
        raise UseCaseError("You can not edit a member from another org.")

    group.remove_member(member)
