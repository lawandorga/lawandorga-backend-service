from typing import Any, List, Optional

from django.db.models import Q
from pydantic import BaseModel, ConfigDict

from core.auth.models import OrgUser
from core.auth.use_cases.rlc_user import confirm_email
from core.permissions.models import HasPermission, Permission
from core.permissions.static import (
    PERMISSION_ADMIN_MANAGE_PERMISSIONS,
    PERMISSION_ADMIN_MANAGE_USERS,
)
from core.seedwork.api_layer import ApiError, Router

from . import schemas

router = Router()


@router.post(url="<int:id>/confirm_email/<str:token>/")
def command__confirm_email(data: schemas.InputConfirmEmail):
    confirm_email(None, data.id, data.token)


# list
@router.get(output_schema=List[schemas.OutputRlcUserSmall])
def list_rlc_users(rlc_user: OrgUser):
    rlc_users = OrgUser.objects.filter(org=rlc_user.org)
    rlc_users_list = list(rlc_users)
    return rlc_users_list


# retrieve
class OutputPermission(BaseModel):
    id: int
    permission_name: str
    source: str
    group_name: str | None
    user_name: str | None
    group_id: int | None

    model_config = ConfigDict(from_attributes=True)


class OutputUser(BaseModel):
    user: schemas.OutputRlcUserOptional
    permissions: Optional[list[OutputPermission]]


@router.get(
    url="<int:id>/",
    output_schema=OutputUser,
)
def retrieve(data: schemas.InputRlcUserGet, rlc_user: OrgUser):
    found_rlc_user = OrgUser.objects.filter(id=data.id).first()
    if found_rlc_user is None:
        raise ApiError("The user could not be found.")

    if found_rlc_user.org != rlc_user.org:
        raise ApiError("The user could not be found.")

    if found_rlc_user.id != rlc_user.id and not rlc_user.has_permission(
        PERMISSION_ADMIN_MANAGE_USERS
    ):
        found_rlc_user_ret: Any = schemas.OutputRlcUserSmall.model_validate(
            found_rlc_user
        ).model_dump()
    else:
        found_rlc_user_ret = found_rlc_user

    permissions: Optional[list[HasPermission]] = None
    if rlc_user.has_permission(PERMISSION_ADMIN_MANAGE_PERMISSIONS):
        queryset = HasPermission.objects.filter(
            Q(user__org=found_rlc_user.org)
            | Q(group_has_permission__from_rlc=found_rlc_user.org)
        )
        queryset = queryset.select_related("permission", "group_has_permission", "user")
        groups = found_rlc_user.groups.all()
        queryset = queryset.filter(
            Q(user=found_rlc_user) | Q(group_has_permission__in=groups)
        )
        permissions = list(queryset)

    return {"user": found_rlc_user_ret, "permissions": permissions}


# activate user
@router.put(
    url="<int:id>/activate/",
    output_schema=schemas.OutputRlcUserSmall,
)
def activate_rlc_user(data: schemas.InputRlcUserActivate, rlc_user: OrgUser):
    rlc_user_to_update = OrgUser.objects.filter(id=data.id).first()
    if rlc_user_to_update is None:
        raise ApiError(
            "The user to be activated could not be found.",
        )

    if not rlc_user.has_permission(PERMISSION_ADMIN_MANAGE_USERS):
        raise ApiError(
            "You need the permission '{}' to do this.".format(
                PERMISSION_ADMIN_MANAGE_USERS
            ),
        )

    if rlc_user.id == rlc_user_to_update.id:
        raise ApiError(
            "You can not activate or deactivate yourself.",
        )

    rlc_user_to_update.activate_or_deactivate()
    rlc_user_to_update.save()

    return rlc_user_to_update


# update settings
@router.put(url="settings_self/")
def update_settings(data: dict[str, Any], rlc_user: OrgUser):
    rlc_user.set_frontend_settings(data)


# get data
@router.get(url="data_self/", output_schema=schemas.OutputRlcUserData)
def query__data(rlc_user: OrgUser):
    data = {
        "user": rlc_user,
        "rlc": rlc_user.org,
        "badges": rlc_user.badges,
        "permissions": rlc_user.get_permissions(),
        "settings": rlc_user.frontend_settings,
    }
    return data


# update user
@router.put(
    url="<int:id>/update_information/",
    output_schema=schemas.OutputRlcUser,
)
def update_user(data: schemas.InputRlcUserUpdate, rlc_user: OrgUser):
    if rlc_user.pk != data.id and not rlc_user.has_permission(
        PERMISSION_ADMIN_MANAGE_USERS
    ):
        error = "You need the permission {} to do this.".format(
            PERMISSION_ADMIN_MANAGE_USERS
        )
        raise ApiError(error)

    rlc_user_to_update = OrgUser.objects.filter(id=data.id).first()
    if rlc_user_to_update is None:
        raise ApiError(
            "The user to be updated could not be found.",
        )

    if rlc_user_to_update.org != rlc_user.org:
        raise ApiError(
            "The user to be updated could not be found.",
        )

    update_data = data.model_dump()
    update_data.pop("id")
    update_data.pop("name")
    rlc_user_to_update.update_information(**update_data)
    rlc_user_to_update.save()
    if data.name:
        rlc_user_to_update.user.name = data.name
        rlc_user_to_update.user.save()

    return rlc_user_to_update


# grant permission
@router.post(url="<int:id>/grant_permission/")
def grant_permission(data: schemas.InputRlcUserGrantPermission, rlc_user: OrgUser):
    rlc_user_to_grant: Optional[OrgUser] = OrgUser.objects.filter(
        id=data.id, org=rlc_user.org
    ).first()

    if rlc_user_to_grant is None:
        raise ApiError(
            "The user you tried to update could not be found.",
        )

    if not rlc_user.has_permission(PERMISSION_ADMIN_MANAGE_PERMISSIONS):
        raise ApiError(
            "You need the permission '{}' to do this.".format(
                PERMISSION_ADMIN_MANAGE_PERMISSIONS
            ),
        )

    permission = Permission.objects.filter(id=data.permission).first()
    if permission is None:
        raise ApiError(
            "The permission you tried to grant could not be found.",
        )

    if rlc_user_to_grant.has_permission(permission):
        raise ApiError("The user already has this permission.")

    rlc_user_to_grant.grant(permission=permission)
