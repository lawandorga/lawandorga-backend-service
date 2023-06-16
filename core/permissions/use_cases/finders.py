from django.db.models import Q

from core.auth.models.org_user import RlcUser
from core.permissions.models import Permission
from core.rlc.models.has_permission import HasPermission
from core.seedwork.use_case_layer import finder_function


@finder_function
def permission_from_id(_, v: int) -> Permission:
    return Permission.objects.get(id=v)


@finder_function
def has_permission_from_id(__actor: RlcUser, v: int) -> HasPermission:
    return HasPermission.objects.get(
        Q(id=v)
        & (Q(user__org=__actor.org) | Q(group_has_permission__from_rlc=__actor.org))
    )
