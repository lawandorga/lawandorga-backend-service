from typing import Optional

from django.db import transaction

from core.auth.domain.user_key import UserKey
from core.auth.models import RlcUser, UserProfile
from core.folders.domain.types import StrDict
from core.seedwork.use_case_layer import use_case


@use_case
def set_password_of_myself(__actor: UserProfile, password: str) -> UserProfile:
    __actor.set_password(password)
    org_user: Optional[RlcUser] = None

    if hasattr(__actor, "rlc_user"):
        org_user = __actor.rlc_user

    if org_user:
        org_user.generate_keys(password)

    with transaction.atomic():
        __actor.save()
        if org_user:
            org_user.save()

    if org_user:
        org_user.lock()
        org_user.save()

    return __actor


@use_case
def run_user_login_checks(__actor: UserProfile, password: str):
    if hasattr(__actor, "rlc_user"):
        rlc_user: RlcUser = __actor.rlc_user

        # generate key if not existent
        if rlc_user.key is None:
            rlc_user.generate_keys(password)
            rlc_user.save()

        # check if key is encrypted
        key: StrDict = rlc_user.key  # type: ignore
        u1 = UserKey.create_from_dict(key)
        if not u1.is_encrypted:
            u2 = u1.encrypt_self(password)
            rlc_user.key = u2.as_dict()
            rlc_user.save()
