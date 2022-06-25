from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from apps.api.models import UserProfile
from apps.static.api_layer import API
from apps.static.service_layer import ServiceResult


class RlcUser(BaseModel):
    id: int
    user_id: int
    birthday: Optional[str]
    phone_int: Optional[str]
    street: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    locked: bool
    email_confirmed: bool
    is_active: bool
    accepted: bool
    updated: datetime
    note: Optional[str]
    name: str
    email: str
    created: datetime
    speciality_of_study: Optional[str]
    speciality_of_study_display: Optional[str]

    class Config:
        orm_mode = True


UNLOCK_RLC_USER_NOT_ALL_KEYS_CORRECT = 'User {} tried to unlock himself, but not all keys are correct.'
UNLOCK_RLC_USER_SUCCESS = 'User {} successfully unlocked himself or herself.'


@API.api(output_schema=RlcUser, auth=True)
def unlock_rlc_user(user: UserProfile):
    if not user.check_all_keys_correct():
        return ServiceResult(UNLOCK_RLC_USER_NOT_ALL_KEYS_CORRECT,
                             error='You can only unlock yourself when all your keys are correct.')
    user.rlc_user.locked = False
    user.rlc_user.save()
    return ServiceResult(UNLOCK_RLC_USER_SUCCESS, user.rlc_user)


@API.split
def rlc_user():
    return {
        "POST": {
            "rlc_users/unlock_self/": unlock_rlc_user,
        },
    }
