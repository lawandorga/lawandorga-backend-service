from django.db.models import Q

from core.auth.models.org_user import OrgUser
from core.permissions.models import HasPermission, Permission
from core.seedwork.use_case_layer import finder_function


@finder_function
def permission_from_id(_, v: int) -> Permission:
    return Permission.objects.get(id=v)


@finder_function
def has_permission_from_id(__actor: OrgUser, v: int) -> HasPermission:
    return HasPermission.objects.get(
        Q(id=v) & (Q(user__org=__actor.org) | Q(group_has_permission__org=__actor.org))
    )
