from datetime import timedelta
from smtplib import SMTPRecipientsRefused
from typing import Any

from django.db import transaction
from django.utils import timezone

from core.auth.models import OrgUser, UserProfile
from core.auth.token_generator import EmailConfirmationTokenGenerator
from core.auth.use_cases.finders import (
    org_from_id_dangerous,
    org_user_from_id,
    org_user_from_id_dangerous,
)
from core.encryption.usecases import fix_keys
from core.legal.models import LegalRequirement, LegalRequirementEvent
from core.permissions.static import PERMISSION_ADMIN_MANAGE_USERS
from core.seedwork.use_case_layer import UseCaseError, use_case
from messagebus.domain.collector import EventCollector


@use_case
def register_org_user(
    __actor: None,
    email: str,
    password: str,
    name: str,
    accepted_legal_requirements: list[int],
    org_id: int,
):
    org = org_from_id_dangerous(__actor, org_id)

    # error validation
    if UserProfile.objects.filter(email=email).exists():
        raise UseCaseError("An account already exists with this email.")

    # user stuff
    user = UserProfile(email=email, name=name)
    user.set_password(password)
    org_user = OrgUser(user=user, email_confirmed=False, org=org)
    org_user.generate_keys(password)

    # legal stuff
    lr_events = []
    for lr in list(LegalRequirement.objects.all()):
        if lr.accept_required and lr.pk not in accepted_legal_requirements:
            raise UseCaseError(
                "You need to accept the legal requirement: '{}'.".format(lr.title)
            )
        event = LegalRequirementEvent(
            legal_requirement=lr,
            user=org_user,
            actor=email,
            accepted=True,
            text="Accepted on registration.",
        )
        lr_events.append(event)

    # save
    with transaction.atomic():
        user.save()
        org_user.save()
        org_user.keyring.store()
        for lre in lr_events:
            lre.save()
        assert org_user.key is not None

    # send confirmation mail
    try:
        org_user.send_email_confirmation_email()
    except SMTPRecipientsRefused:
        user.delete()
        raise UseCaseError(
            "We could not send a confirmation email to this address. "
            "Please check if this email is correct."
        )


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_USERS])
def delete_user(__actor: OrgUser, other_user_id: int):
    other_user = org_user_from_id(__actor, other_user_id)
    delete_safe, folders = other_user.check_delete_is_safe()
    if not delete_safe:
        raise UseCaseError(
            "You can not delete this user right now, because "
            f"you could loose access to the following folders: '{folders}'. "
            "\nThis user is one of the only two "
            "persons with access to this folders. \n"
            "In order to delete this user, you need to add another user to these folders."
        )
    other_user.user.delete()


@use_case
def confirm_email(__actor: None, org_user_id: int, token: str):
    org_user = org_user_from_id_dangerous(__actor, org_user_id)
    org_user.confirm_email(EmailConfirmationTokenGenerator, token)
    org_user.save()


@use_case
def unlock_user(__actor: OrgUser, another_org_user_id: int, collector: EventCollector):
    another_org_user = org_user_from_id(__actor, another_org_user_id)

    one_year_ago = timezone.now() - timedelta(days=365)
    if (
        another_org_user.user.last_login
        and another_org_user.user.last_login < one_year_ago
    ):
        raise UseCaseError(
            "The user has not logged in for over one year and can therefore not be accepted. Either delete the user or tell the user to login again."
        )

    fix_keys(__actor, another_org_user.pk)
    another_org_user.unlock(__actor, collector)
    another_org_user.save()


@use_case
def unlock_myself(__actor: OrgUser):
    __actor.user.users_rlc_keys.get().test(__actor.keyring.get_private_key())
    if not __actor.all_keys_correct:
        raise UseCaseError(
            "You can only unlock yourself when all your keys are correct.",
        )
    __actor.locked = False
    __actor.save()


@use_case
def update_user_data(
    __actor: OrgUser,
    other_user_id: int,
    name: str | None = None,
    phone_number: str | None = None,
    street: str | None = None,
    city: str | None = None,
    postal_code: str | None = None,
    speciality_of_study: str | None = None,
    note: str | None = None,
    qualifications: list[str] | None = None,
):
    if __actor.pk != other_user_id and not __actor.has_permission(
        PERMISSION_ADMIN_MANAGE_USERS
    ):
        error = "You need the permission {} to do this.".format(
            PERMISSION_ADMIN_MANAGE_USERS
        )
        raise UseCaseError(error)

    org_user_to_update = OrgUser.objects.get(org_id=__actor.org_id, id=other_user_id)
    if org_user_to_update is None:
        raise UseCaseError(
            "The user to be updated could not be found.",
        )

    if org_user_to_update.org != __actor.org:
        raise UseCaseError(
            "The user to be updated could not be found.",
        )

    org_user_to_update.update_information(
        street=street,
        speciality_of_study=speciality_of_study,
        postal_code=postal_code,
        city=city,
        phone_number=phone_number,
        note=note,
        qualifications=qualifications,
    )
    org_user_to_update.save()
    if name:
        org_user_to_update.user.name = name
        org_user_to_update.user.save()

    return org_user_to_update


@use_case
def update_frontend_settings(__actor: OrgUser, data: dict[str, Any]):
    __actor.set_frontend_settings(data)


@use_case
def activate_org_user(__actor: OrgUser, other_user_id: int):
    org_user_to_update = OrgUser.objects.filter(id=other_user_id).first()
    if org_user_to_update is None:
        raise UseCaseError(
            "The user to be activated could not be found.",
        )

    if not __actor.has_permission(PERMISSION_ADMIN_MANAGE_USERS):
        raise UseCaseError(
            "You need the permission '{}' to do this.".format(
                PERMISSION_ADMIN_MANAGE_USERS
            ),
        )

    if __actor.pk == org_user_to_update.pk:
        raise UseCaseError(
            "You can not activate or deactivate yourself.",
        )

    org_user_to_update.activate_or_deactivate()
    org_user_to_update.save()

    return org_user_to_update
