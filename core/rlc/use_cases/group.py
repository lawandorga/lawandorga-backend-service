from core.auth.models import OrgUser
from core.auth.use_cases.finders import rlc_user_from_id
from core.permissions.static import PERMISSION_ADMIN_MANAGE_GROUPS
from core.rlc.models import Group
from core.rlc.use_cases.finders import group_from_id
from core.seedwork.use_case_layer import UseCaseError, use_case


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_GROUPS])
def create_group(__actor: OrgUser, name: str, description: str = "") -> Group:
    group = Group.create(org=__actor.org, name=name, description=description)
    group.save()
    group.add_member(__actor)
    group.generate_keys()
    group.save()
    return group


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_GROUPS])
def update_group(__actor: OrgUser, group_id: int, name: str, description: str | None):
    group = group_from_id(__actor, group_id)
    group.update_information(name=name, description=description)
    group.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_GROUPS])
def delete_group(__actor: OrgUser, group_id: int):
    group = group_from_id(__actor, group_id)
    group.delete()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_GROUPS])
def add_member_to_group(__actor: OrgUser, group_id: int, new_member_id: int):
    group = group_from_id(__actor, group_id)
    if not group.has_keys(__actor):
        raise UseCaseError(
            "You do not have keys for this group. Therefore you can not add members. "
            "You need to be part of this group in order to add members."
        )

    new_member = rlc_user_from_id(__actor, new_member_id)

    if group.from_rlc_id != new_member.org_id:
        raise UseCaseError("You can not edit a member from another org.")

    group.add_member(new_member, by=__actor)


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_GROUPS])
def remove_member_from_group(__actor: OrgUser, group_id: int, member_id: int):
    group = group_from_id(__actor, group_id)

    if group.members.count() <= 2:
        raise UseCaseError(
            "You can not remove the last members of a group. "
            "But you can always delete the group."
        )

    member = rlc_user_from_id(__actor, member_id)

    if group.from_rlc_id != member.org_id:
        raise UseCaseError("You can not edit a member from another org.")

    group.remove_member(member)
