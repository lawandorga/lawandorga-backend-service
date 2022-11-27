from smtplib import SMTPRecipientsRefused

from django.db import transaction

from core.auth.models import RlcUser, UserProfile
from core.auth.use_cases.finders import org_from_id

# from core.legal.models import LegalRequirement, LegalRequirementUser, LegalRequirementEvent
from core.seedwork.use_case_layer import UseCaseError, find, use_case


@use_case
def register_rlc_user(
    __actor: None,
    email: str,
    password: str,
    name: str,
    # accepted_legal_requirements: list[int],
    org=find(org_from_id),
):
    # user stuff
    user = UserProfile(email=email, name=name)
    user.set_password(password)
    rlc_user = RlcUser(user=user, email_confirmed=False, org=org)
    rlc_user.generate_keys(password)

    # legal stuff
    # lr_users = []
    # for lr in list(LegalRequirement.objects.all()):
    #     if lr.accept_required and lr.pk not in accepted_legal_requirements:
    #         raise UseCaseError('You need to accept the legal requirement: .')
    #     lr_user = LegalRequirementUser(legal_requirement=lr, rlc_user=rlc_user)
    #     lr_users.append(lr_user)
    # lr_events = []
    # for pk in accepted_legal_requirements:
    #     lr_event = LegalRequirementEvent()

    # save
    with transaction.atomic():
        user.save()
        rlc_user.save()
        # for lr in lr_users:
        #     lr.save()
        # for lr in lr_events:
        #     lr.save()
        assert rlc_user.key is not None

    # send confirmation mail
    try:
        rlc_user.send_email_confirmation_email()
    except SMTPRecipientsRefused:
        user.delete()
        raise UseCaseError(
            "We could not send a confirmation email to this address. "
            "Please check if this email is correct."
        )
