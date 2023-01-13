from uuid import UUID

from django.db.models import Q

from core.mail.models import MailAddress, MailDomain, MailUser
from core.mail.models.group import MailGroup
from core.seedwork.use_case_layer import finder_function


@finder_function
def mail_domain_from_uuid(actor: MailUser, v: UUID) -> MailDomain:
    return MailDomain.objects.filter(uuid=v).get(org__id=actor.org_id)


@finder_function
def mail_address_from_uuid(actor: MailUser, v: UUID) -> MailAddress:
    return MailAddress.objects.get(
        Q(
            Q(uuid=v)
            & (
                Q(account__user__org__id=actor.org_id)
                | Q(account__group__org__id=actor.org_id)
            )
        )
    )


@finder_function
def mail_user_from_uuid(actor: MailUser, v: UUID) -> MailUser:
    return MailUser.objects.get(uuid=v, org__id=actor.org_id)


@finder_function
def mail_group_from_uuid(actor: MailUser, v: UUID) -> MailGroup:
    return MailGroup.objects.get(uuid=v, org_id=actor.org_id)
