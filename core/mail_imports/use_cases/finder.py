from uuid import UUID

from core.auth.models import OrgUser
from core.mail_imports.models.mail_import import MailImport
from core.seedwork.use_case_layer import finder_function


@finder_function
def mails_from_uuids(actor: OrgUser, uuids: list[UUID]) -> list[MailImport]:
    return list(MailImport.objects.filter(org=actor.org, uuid__in=uuids))


@finder_function
def mail_from_uuid(actor: OrgUser, uuid: UUID) -> MailImport:
    return MailImport.objects.get(org=actor.org, uuid=uuid)
