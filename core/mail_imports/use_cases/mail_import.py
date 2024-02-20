from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.seedwork.use_case_layer import use_case


@use_case
def mark_emails_as_read(__actor: OrgUser, email_uuids: list[UUID]):
    pass
