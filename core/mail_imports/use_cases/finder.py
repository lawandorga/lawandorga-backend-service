from uuid import UUID

from core.auth.models import OrgUser
from core.mail_imports.models.mail_import import MailImport
from core.seedwork.use_case_layer import finder_function


@finder_function
def mails_from_uuids(_: OrgUser, uuids: list[UUID]) -> list[MailImport]:
    return list(MailImport.objects.filter(uuid__in=uuids))
