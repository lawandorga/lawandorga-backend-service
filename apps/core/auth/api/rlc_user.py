from typing import Any, Dict

from apps.static.api_layer import Router
from apps.static.service_layer import ServiceResult

from ...static import PERMISSION_ADMIN_MANAGE_USERS
from ..models import RlcUser
from . import schemas

router = Router()


# retrieve
RETRIEVE_SUCCESS = "User {} has successfully retrieved some user."
RETRIEVE_ERROR_NOT_FOUND = 'User {} tried to retrieve a user that could not be found.'
RETRIEVE_ERROR_ANOTHER_RLC = 'User {} tried to retrieve a user from another rlc.'


@router.get(url="<int:pk>/", input_schema=schemas.InputRlcUserGet, output_schema=RlcUser)
def retrieve(data: schemas.InputRlcUserGet, rlc_user: RlcUser):
    found_rlc_user = RlcUser.objects.filter(id=data.id).first()
    if found_rlc_user is None:
        return ServiceResult(
            RETRIEVE_ERROR_NOT_FOUND,
            error="The user could not be found.",
        )

    if found_rlc_user.org != rlc_user.org:
        return ServiceResult(RETRIEVE_ERROR_ANOTHER_RLC, error="The user could not be found.")

    return ServiceResult(RETRIEVE_SUCCESS, found_rlc_user)


# unlock user
UNLOCK_RLC_USER_NOT_ALL_KEYS_CORRECT = (
    "User {} tried to unlock himself, but not all keys are correct."
)
UNLOCK_RLC_USER_SUCCESS = "User {} successfully unlocked himself or herself."


@router.api(method="POST", url="unlock_self/", output_schema=schemas.RlcUser)
def unlock_rlc_user(rlc_user: RlcUser):
    if not rlc_user.user.check_all_keys_correct():
        return ServiceResult(
            UNLOCK_RLC_USER_NOT_ALL_KEYS_CORRECT,
            error="You can only unlock yourself when all your keys are correct.",
        )
    rlc_user.locked = False
    rlc_user.save()
    return ServiceResult(UNLOCK_RLC_USER_SUCCESS, rlc_user)


# update settings
UPDATE_SETTINGS_SUCCESS = (
    "User {} has successfully updated his or her frontend settings."
)


@router.put(url="settings_self/", input_schema=Dict[str, Any])
def update_settings(data: Dict[str, Any], rlc_user: RlcUser):
    rlc_user.set_frontend_settings(data)
    return ServiceResult(UPDATE_SETTINGS_SUCCESS)


# get data
DATA_RLC_USER_SUCCESS = "User {} successfully requested data about himself or herself."


@router.get(url="data_self/", output_schema=schemas.RlcUserData)
def get_data(rlc_user: RlcUser):
    data = {
        "user": rlc_user,
        "rlc": rlc_user.org,
        "badges": rlc_user.get_badges(),
        "permissions": rlc_user.user.get_all_user_permissions(),
        "settings": rlc_user.frontend_settings,
    }
    return ServiceResult(DATA_RLC_USER_SUCCESS, data)


# update user
UPDATE_USER_SUCCESS = "User {} has successfully updated some user."
UPDATE_USER_ERROR_FORBIDDEN = (
    "User {} tried to update another user, but is not allowed to do so."
)
UPDATE_USER_ERROR_WRONG_ORG = "User {} tried to update some user from another org."
UPDATE_USER_ERROR_USER_NOT_FOUND = (
    "User {} tried to update another user that does not exist."
)


@router.put(
    url="<int:id>/update_information/",
    input_schema=schemas.InputRlcUserUpdate,
    output_schema=schemas.RlcUser,
)
def update_user(data: schemas.InputRlcUserUpdate, rlc_user: RlcUser):
    if rlc_user.pk != data.id and not rlc_user.has_permission(
        PERMISSION_ADMIN_MANAGE_USERS
    ):
        error = "You need the permission {} to do this.".format(
            PERMISSION_ADMIN_MANAGE_USERS
        )
        return ServiceResult(UPDATE_USER_ERROR_FORBIDDEN, error=error)

    rlc_user_to_update = RlcUser.objects.filter(id=data.id).first()
    if rlc_user_to_update is None:
        return ServiceResult(
            UPDATE_USER_ERROR_USER_NOT_FOUND,
            error="The user to be updated could not be found.",
        )

    if rlc_user_to_update.org != rlc_user.org:
        return ServiceResult(
            UPDATE_USER_ERROR_WRONG_ORG,
            error="The user to be updated could not be found.",
        )

    update_data = data.dict()
    update_data.pop("id")
    update_data.pop("name")
    rlc_user_to_update.update_information(**update_data)
    rlc_user_to_update.save()
    if data.name:
        rlc_user_to_update.user.name = data.name
        rlc_user_to_update.user.save()

    return ServiceResult(UPDATE_USER_SUCCESS, rlc_user_to_update)
