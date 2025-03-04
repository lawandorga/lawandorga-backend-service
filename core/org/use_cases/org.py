from core.auth.models import OrgUser
from core.auth.use_cases.finders import org_user_from_id
from core.permissions.static import PERMISSION_ADMIN_MANAGE_USERS
from core.seedwork.use_case_layer import use_case


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_USERS])
def accept_member_to_org(__actor: OrgUser, user_id: int):
    user = org_user_from_id(__actor, user_id)
    __actor.org.accept_member(__actor, user)
