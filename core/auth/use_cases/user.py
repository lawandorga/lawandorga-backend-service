from typing import Optional

from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.db import transaction

from core.auth.domain.user_key import UserKey
from core.auth.models import OrgUser, UserProfile
from core.seedwork.use_case_layer import UseCaseError, use_case

from seedwork.types import JsonDict


@use_case
def set_password_of_myself(__actor: UserProfile, password: str) -> UserProfile:
    __actor.set_password(password)
    org_user: Optional[OrgUser] = None

    if hasattr(__actor, "org_user"):
        org_user = __actor.org_user

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
    if hasattr(__actor, "org_user"):
        org_user: OrgUser = __actor.org_user

        # generate key if not existent
        if org_user.key is None or org_user.key == {}:
            org_user.generate_keys(password)
            org_user.save()

        # check if key is encrypted
        key: JsonDict = org_user.key  # type: ignore
        u1 = UserKey.create_from_dict(key)
        if not u1.is_encrypted:
            u2 = u1.encrypt_self(password)
            org_user.key = u2.as_dict()
            org_user.save()


@use_case
def change_password_of_user(
    __actor: UserProfile,
    current_password: str,
    new_password: str,
    new_password_confirm: str,
):
    if not new_password == new_password_confirm:
        raise UseCaseError("The new passwords do not match.")

    try:
        validate_password(new_password)
    except exceptions.ValidationError as e:
        raise UseCaseError(e.messages[0])

    if not __actor.check_password(current_password):
        raise UseCaseError("Your current password is not correct.")

    objs = __actor.change_password(current_password, new_password)
    [obj.save() for obj in objs]
