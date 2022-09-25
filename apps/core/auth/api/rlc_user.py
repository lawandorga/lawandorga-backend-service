from typing import Any, Dict

from apps.core.models import UserProfile
from apps.static.api_layer import Router
from apps.static.service_layer import ServiceResult

from ..models import RlcUser
from . import schemas

router = Router()

# unlock user
UNLOCK_RLC_USER_NOT_ALL_KEYS_CORRECT = (
    "User {} tried to unlock himself, but not all keys are correct."
)
UNLOCK_RLC_USER_SUCCESS = "User {} successfully unlocked himself or herself."


@router.api(method="POST", url="unlock_self/", output_schema=schemas.RlcUser, auth=True)
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


@router.api(method="PUT", url="settings_self/", auth=True, input_schema=Dict[str, Any])
def update_settings(data: Dict[str, Any], rlc_user: RlcUser):
    rlc_user.set_frontend_settings(data)
    return ServiceResult(UPDATE_SETTINGS_SUCCESS)


# get data
DATA_RLC_USER_SUCCESS = "User {} successfully requested data about himself or herself."


@router.api(
    method="GET", url="data_self/", output_schema=schemas.RlcUserData, auth=True
)
def get_data(rlc_user: RlcUser):
    data = {
        "user": rlc_user,
        "rlc": rlc_user.org,
        "badges": rlc_user.get_badges(),
        "permissions": rlc_user.user.get_all_user_permissions(),
        "settings": rlc_user.frontend_settings,
    }
    return ServiceResult(DATA_RLC_USER_SUCCESS, data)
