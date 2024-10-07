from uuid import uuid4

from django.core.files.base import ContentFile

from core.mail_imports.models.mail_import import MailAttachment, MailImport
from core.seedwork import test_helpers


def test_mark_as_read_works():
    folder_uuid = uuid4()
    mail = MailImport.create(
        sender="test@law-orga.de",
        to="recieve@law-orag.de",
        content="Test Mail",
        folder_uuid=folder_uuid,
        subject="Test Mail",
        org_id=0,
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
    )
    assert not mail.is_pinned
    mail.toggle_pinned()
    assert mail.is_pinned
    mail.toggle_pinned()
    assert not mail.is_pinned


def test_encryption(db):
    u = test_helpers.create_org_user()
    user = u["rlc_user"]
    folder = test_helpers.create_folder(user=user)
    folder_uuid = folder["folder"].uuid
    mail = MailImport.create(
        sender="test@law-orga.de",
        to="recieve@law-orag.de",
        content="Test Mail",
        folder_uuid=folder_uuid,
        subject="Test Mail",
        org_id=user.org_id,
    )
    mail.encrypt(user)
    mail.save()
    mail = MailImport.objects.get(uuid=mail.uuid)
    mail.decrypt(user)
    assert mail.content == "Test Mail"
    assert mail.subject == "Test Mail"


def test_attachement_encrypts(db):
    u = test_helpers.create_org_user()
    user = u["rlc_user"]
    folder = test_helpers.create_folder(user=user)
    folder_uuid = folder["folder"].uuid
    mail = MailImport.create(
        sender="test@law-orga.de",
        to="recieve@law-orag.de",
        content="Test Mail",
        folder_uuid=folder_uuid,
        subject="Test Mail",
        org_id=user.org_id,
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
