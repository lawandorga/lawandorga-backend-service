from uuid import uuid4

from core.mail_imports.models.mail_import import MailImport


def test_mark_as_read_works():
    folder_uuid = uuid4()
    mail = MailImport.create(
        sender="test@law-orga.de",
        content="Test Mail",
        folder_uuid=folder_uuid,
        subject="Test Mail",
    )
    mail.mark_as_read()
    assert mail.is_read

def test_mark_as_pinned_works():
    folder_uuid = uuid4()
    mail = MailImport.create(
        sender="test@law-orga.de",
        content="Test Mail",
        folder_uuid=folder_uuid,
        subject="Test Mail",
    )
    mail.mark_as_pinned()
    assert mail.is_pinned