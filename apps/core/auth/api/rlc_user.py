from typing import Any, Dict, List, Optional

from apps.core.auth.api import schemas
from apps.core.auth.models import RlcUser
from apps.core.rlc.models import Permission
from apps.core.static import (
    PERMISSION_ADMIN_MANAGE_PERMISSIONS,
    PERMISSION_ADMIN_MANAGE_USERS,
)
from apps.static.api_layer import ApiError, Router

router = Router()


# list
@router.get(output_schema=List[schemas.OutputRlcUserSmall])
def list_rlc_users(rlc_user: RlcUser):
    rlc_users = RlcUser.objects.filter(org=rlc_user.org)
    rlc_users_list = list(rlc_users)
    return rlc_users_list


# retrieve
@router.get(
    url="<int:id>/",
    input_schema=schemas.InputRlcUserGet,
    output_schema=schemas.OutputRlcUserOptional,
)
def retrieve(data: schemas.InputRlcUserGet, rlc_user: RlcUser):
    found_rlc_user = RlcUser.objects.filter(id=data.id).first()
    if found_rlc_user is None:
        raise ApiError("The user could not be found.")

    if found_rlc_user.org != rlc_user.org:
        raise ApiError("The user could not be found.")

    if found_rlc_user.id != rlc_user.id and not rlc_user.has_permission(
        PERMISSION_ADMIN_MANAGE_USERS
    ):
        found_rlc_user_ret: Any = schemas.OutputRlcUserSmall.from_orm(
            found_rlc_user
        ).dict()
    else:
        found_rlc_user_ret = found_rlc_user

    return found_rlc_user_ret


# unlock user
@router.api(method="POST", url="unlock_self/", output_schema=schemas.OutputRlcUser)
def unlock_rlc_user(rlc_user: RlcUser):
    if not rlc_user.user.check_all_keys_correct():
        raise ApiError(
            "You can only unlock yourself when all your keys are correct.",
        )
    rlc_user.locked = False
    rlc_user.save()
    return rlc_user


# activate user
@router.post(
    url="<int:id>/activate/",
    input_schema=schemas.InputRlcUserActivate,
    output_schema=schemas.OutputRlcUserSmall,
)
def activate_rlc_user(data: schemas.InputRlcUserActivate, rlc_user: RlcUser):
    rlc_user_to_update = RlcUser.objects.filter(id=data.id).first()
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
@router.put(url="settings_self/", input_schema=Dict[str, Any])
def update_settings(data: Dict[str, Any], rlc_user: RlcUser):
    rlc_user.set_frontend_settings(data)


# get data
@router.get(url="data_self/", output_schema=schemas.OutputRlcUserData)
def get_data(rlc_user: RlcUser):
    data = {
        "user": rlc_user,
        "rlc": rlc_user.org,
        "badges": rlc_user.get_badges(),
        "permissions": rlc_user.get_permissions(),
        "settings": rlc_user.frontend_settings,
    }
    return data


# update user
@router.put(
    url="<int:id>/update_information/",
    input_schema=schemas.InputRlcUserUpdate,
    output_schema=schemas.OutputRlcUser,
)
def update_user(data: schemas.InputRlcUserUpdate, rlc_user: RlcUser):
    if rlc_user.pk != data.id and not rlc_user.has_permission(
        PERMISSION_ADMIN_MANAGE_USERS
    ):
        error = "You need the permission {} to do this.".format(
            PERMISSION_ADMIN_MANAGE_USERS
        )
        raise ApiError(error)

    rlc_user_to_update = RlcUser.objects.filter(id=data.id).first()
    if rlc_user_to_update is None:
        raise ApiError(
            "The user to be updated could not be found.",
        )

    if rlc_user_to_update.org != rlc_user.org:
        raise ApiError(
            "The user to be updated could not be found.",
        )

    update_data = data.dict()
    update_data.pop("id")
    update_data.pop("name")
    rlc_user_to_update.update_information(**update_data)
    rlc_user_to_update.save()
    if data.name:
        rlc_user_to_update.user.name = data.name
        rlc_user_to_update.user.save()

    return rlc_user_to_update


# grant permission
@router.post(
    url="<int:id>/grant_permission/", input_schema=schemas.InputRlcUserGrantPermission
)
def grant_permission(data: schemas.InputRlcUserGrantPermission, rlc_user: RlcUser):
    rlc_user_to_grant: Optional[RlcUser] = RlcUser.objects.filter(
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
