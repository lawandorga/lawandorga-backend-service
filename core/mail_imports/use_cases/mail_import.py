from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.seedwork.use_case_layer import use_case


@use_case
def mark_mails_as_read(__actor: OrgUser, mail_uuids: list[UUID]):
    print("marking mails", mail_uuids, "as read")
    pass


@use_case
def mark_mail_as_pinned(__actor: OrgUser, mail_uuid: UUID):
    print("toggling mail", mail_uuid, "as pinned")
    pass
