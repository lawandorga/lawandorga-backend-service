from uuid import uuid4

from django.core.files.base import ContentFile

from core.mail_imports.models.mail_import import MailAttachment, MailImport
from core.tests import test_helpers

SENDING_DATETIME = "2026-01-01T00:00:00+00:00"


def test_mark_as_read_works():
    folder_uuid = uuid4()
    mail = MailImport.create(
        sender="test@law-orga.de",
        to="recieve@law-orag.de",
        content="Test Mail",
        folder_uuid=folder_uuid,
        subject="Test Mail",
        org_id=0,
        sending_datetime=SENDING_DATETIME,
    )
    mail.mark_as_read()
    assert mail.is_read


def test_mark_as_unread_works():
    folder_uuid = uuid4()
    mail = MailImport.create(
        sender="test@law-orga.de",
        to="recieve@law-orag.de",
        content="Test Mail",
        folder_uuid=folder_uuid,
        subject="Test Mail",
        org_id=0,
        sending_datetime=SENDING_DATETIME,
    )
    mail.mark_as_unread()
    assert not mail.is_read


def test_mark_as_pinned_works():
    folder_uuid = uuid4()
    mail = MailImport.create(
        sender="test@law-orga.de",
        to="recieve@law-orag.de",
        content="Test Mail",
        folder_uuid=folder_uuid,
        subject="Test Mail",
        org_id=0,
        sending_datetime=SENDING_DATETIME,
    )
    mail.toggle_pinned()
    assert mail.is_pinned


def test_mark_as_unpinned_works():
    folder_uuid = uuid4()
    mail = MailImport.create(
        sender="test@law-orga.de",
        to="recieve@law-orag.de",
        content="Test Mail",
        folder_uuid=folder_uuid,
        subject="Test Mail",
        org_id=0,
        sending_datetime=SENDING_DATETIME,
    )
    assert not mail.is_pinned
    mail.toggle_pinned()
    assert mail.is_pinned
    mail.toggle_pinned()
    assert not mail.is_pinned


def test_encryption(db):
    u = test_helpers.create_org_user()
    user = u["org_user"]
    folder = test_helpers.create_folder(user=user)
    folder_uuid = folder["folder"].uuid
    mail = MailImport.create(
        sender="test@law-orga.de",
        to="recieve@law-orag.de",
        content="Test Mail",
        folder_uuid=folder_uuid,
        subject="Test Mail",
        org_id=user.org_id,
        sending_datetime=SENDING_DATETIME,
    )
    mail.encrypt(user)
    mail.save()
    mail = MailImport.objects.get(uuid=mail.uuid)
    mail.decrypt(user)
    assert mail.content == "Test Mail"
    assert mail.subject == "Test Mail"


def test_long_email_headers_are_truncated_to_255_characters(db):
    u = test_helpers.create_org_user()
    user = u["org_user"]
    folder = test_helpers.create_folder(user=user)
    headers = {
        "sender": "s" * 256,
        "to": "t" * 260,
        "cc": "c" * 270,
        "bcc": "b" * 280,
    }
    mail = MailImport.create(
        **headers,
        content="Test Mail",
        folder_uuid=folder["folder"].uuid,
        subject="Test Mail",
        org_id=user.org_id,
        sending_datetime=SENDING_DATETIME,
    )
    mail.encrypt(user)
    mail.save()

    saved_mail = MailImport.objects.get(uuid=mail.uuid)
    for field, value in headers.items():
        saved_value = getattr(saved_mail, field)
        assert len(saved_value) == 255
        assert saved_value == value[:252] + "..."


def test_attachement_encrypts(db):
    u = test_helpers.create_org_user()
    user = u["org_user"]
    folder = test_helpers.create_folder(user=user)
    folder_uuid = folder["folder"].uuid
    mail = MailImport.create(
        sender="test@law-orga.de",
        to="recieve@law-orag.de",
        content="Test Mail",
        folder_uuid=folder_uuid,
        subject="Test Mail",
        org_id=user.org_id,
        sending_datetime=SENDING_DATETIME,
    )
    mail.encrypt(user)
    mail.save()
    file = ContentFile(b"this is a custom test", "test.txt")
    attachement = MailAttachment.create(
        mail_import=mail, filename="test.txt", content=file, user=user
    )
    attachement.save()
    assert attachement.content != "this is a custom test"
    assert attachement.get_decrypted_file(user).read() == b"this is a custom test"
