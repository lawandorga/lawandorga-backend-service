from core.auth.models import RlcUser
from core.auth.use_cases.finders import rlc_user_from_id
from core.seedwork.use_case_layer import find, use_case
from core.static import PERMISSION_ADMIN_MANAGE_USERS


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_USERS])
def accept_member_to_org(__actor: RlcUser, user=find(rlc_user_from_id)):
    __actor.org.accept_member(__actor, user)
