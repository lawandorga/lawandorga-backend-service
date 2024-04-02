from uuid import uuid4

from core.mail_imports.models.mail_import import MailImport
from core.mail_imports.use_cases.mail_import import mark_mails_as_read
from core.seedwork import test_helpers


def test_mails_can_be_marked_as_read(db):
    u = test_helpers.create_org_user()
    user = u["rlc_user"]
    folder_uuid = uuid4()
    mail = MailImport(
        sender="test@law-orga.de",
        content="Test Mail",
        folder_uuid=folder_uuid,
        subject="Test Mail",
        org_id=user.org_id,
    )
    mail.save()
    mark_mails_as_read(user, [mail.uuid])
    mail.refresh_from_db()
    assert mail.is_read
