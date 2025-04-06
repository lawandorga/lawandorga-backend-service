from core.auth.models import OrgUser
from core.auth.use_cases.finders import org_from_id, org_user_from_id
from core.org.models.org import Org
from core.org.use_cases.finders import group_from_id
from core.permissions.static import (
    PERMISSION_ADMIN_MANAGE_GROUPS,
    PERMISSION_ADMIN_MANAGE_USERS,
)
from core.seedwork.use_case_layer import use_case


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_USERS])
def accept_member_to_org(__actor: OrgUser, user_id: int):
    user = org_user_from_id(__actor, user_id)
    org: Org = __actor.org
    org.accept_member(__actor, user)
    group = org.default_group_for_new_users
    if group:
        group.add_member(new_member=user, by=__actor)
        group.refresh_from_db()
        assert group.has_member(user)


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_GROUPS])
def update_org(
    __actor: OrgUser,
    org_id: int,
    org_name: str,
    default_group_for_new_users_id: int | None,
    is_mail_enabled: bool,
    is_events_enabled: bool,
    is_chat_enabled: bool,
    user_qualifications: list[str],
):
    org = org_from_id(__actor, org_id)
    group = (
        group_from_id(__actor, default_group_for_new_users_id)
        if default_group_for_new_users_id
        else None
    )
    org.update(
        name=org_name,
        default_group_for_new_users=group,
        is_mail_enabled=is_mail_enabled,
        is_events_enabled=is_events_enabled,
        is_chat_enabled=is_chat_enabled,
        user_qualifications=user_qualifications,
    )
    org.save()
