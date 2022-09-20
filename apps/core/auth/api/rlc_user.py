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
def unlock_rlc_user(user: UserProfile):
    if not user.check_all_keys_correct():
        return ServiceResult(
            UNLOCK_RLC_USER_NOT_ALL_KEYS_CORRECT,
            error="You can only unlock yourself when all your keys are correct.",
        )
    user.rlc_user.locked = False
    user.rlc_user.save()
    return ServiceResult(UNLOCK_RLC_USER_SUCCESS, user.rlc_user)


# update settings
def update_settings(rlc_user: RlcUser):
    pass


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
