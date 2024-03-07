from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.seedwork.use_case_layer import use_case


@use_case
def mark_emails_as_read(__actor: OrgUser, email_uuids: list[UUID]):
    print("marking emails", email_uuids, "as read")
    pass


@use_case
def mark_email_as_pinned(__actor: OrgUser, email_uuid: UUID):
    print("toggling email", email_uuid, "as pinned")
    pass
