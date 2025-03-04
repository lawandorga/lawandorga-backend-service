from core.auth.models.org_user import OrgUser
from core.auth.use_cases.finders import rlc_user_from_id
from core.org.use_cases.finders import group_from_id
from core.permissions.models import HasPermission
from core.permissions.static import PERMISSION_ADMIN_MANAGE_PERMISSIONS
from core.permissions.use_cases.finders import (
    has_permission_from_id,
    permission_from_id,
)
from core.seedwork.use_case_layer import UseCaseError, use_case


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_PERMISSIONS])
def create_has_permission(
    __actor: OrgUser, user_id: int | None, group_id: int | None, permission_id: int
):
    if user_id is None and group_id is None:
        raise UseCaseError("You must specify a user or a group.")

    if user_id is not None and group_id is not None:
        raise UseCaseError("You can not specify a user and a group.")

    permission = permission_from_id(__actor, permission_id)

    if user_id is not None:
        user = rlc_user_from_id(__actor, user_id)
        has_permission = HasPermission.create(user=user, permission=permission)
        has_permission.save()

    if group_id is not None:
        group = group_from_id(__actor, group_id)
        has_permission = HasPermission.create(group=group, permission=permission)
        has_permission.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_PERMISSIONS])
def delete_has_permission(__actor: OrgUser, has_permission_id: int):
    has_permission = has_permission_from_id(__actor, has_permission_id)
    has_permission.delete()
