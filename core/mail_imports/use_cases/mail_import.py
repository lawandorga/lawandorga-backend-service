from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.mail_imports.models.mail_import import MailImport
from core.mail_imports.use_cases.finder import mail_from_uuid, mails_from_uuids
from core.seedwork.use_case_layer import use_case


@use_case
def mark_mails_as_read(__actor: OrgUser, mail_uuids: list[UUID]):
    mails = mails_from_uuids(__actor, mail_uuids)
    for mail in mails:
        mail.mark_as_read()
    MailImport.objects.bulk_update(mails, ["is_read"])


@use_case
def toggle_mail_pinned(__actor: OrgUser, mail_uuid: UUID):
    mail = mail_from_uuid(__actor, mail_uuid)
    mail.mark_as_pinned()
    MailImport.objects.update()
