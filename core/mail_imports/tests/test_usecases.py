from email.message import Message
from uuid import uuid4

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from core.mail_imports.models.mail_import import MailAttachment, MailImport
from core.mail_imports.use_cases.mail_import import (
    AssignedEmail,
    ValidatedEmail,
    assign_email_to_folder_uuid,
    delete_mail,
    get_addresses_from_message,
    mark_mails_as_read,
    toggle_mail_pinned,
)
from core.seedwork import test_helpers


def test_mail_can_be_pinned(db):
    u = test_helpers.create_org_user()
    user = u["org_user"]
    folder = test_helpers.create_folder(user=user)
    folder_uuid = folder["folder"].uuid
    mail = MailImport.create(
        sender="test@law-orga.de",
        to="recieve@law-orga.de",
        content="Test Mail",
        folder_uuid=folder_uuid,
        subject="Test Mail",
        org_id=user.org_id,
    )
    mail.encrypt(user)
    mail.save()
    toggle_mail_pinned(user, mail.uuid)
    mail.refresh_from_db()
    assert mail.is_pinned


def test_mails_can_be_marked_as_read(db):
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
    )
    mail.encrypt(user)
    mail.save()
    mark_mails_as_read(user, [mail.uuid])
    mail.refresh_from_db()
    assert mail.is_read


def test_assigned_email_not_created_without_folder_uuid():
    email = ValidatedEmail(
        uid="1",
        sender="Sender",
        to="To",
        cc="",
        bcc="",
        date="",
        subject="Test",
        content="Test",
        addresses=[],
    )
    res = assign_email_to_folder_uuid(email)
    assert res == email


def test_assigned_email_is_created_with_folder_uuid():
    uuid2 = uuid4()
    email = ValidatedEmail(
        uid="1",
        sender="Sender",
        to="To",
        cc="",
        bcc="",
        date="",
        subject="Test",
        content="Test",
        addresses=[f"{uuid2}@law-orga.de"],
    )
    res = assign_email_to_folder_uuid(email)
    new = AssignedEmail(folder_uuids=[uuid2], **email.model_dump())
    assert res != email
    assert res == new


def test_get_addresses_from_message():
    msg = Message()
    msg["Subject"] = "Test Subject"
    msg["From"] = "from@law-orga.de"
    msg["To"] = "recipient1@law-orga.de"
    msg["Cc"] = "recipient2@law-orga.de"
    msg["Bcc"] = "recipient3@law-orga.de"
    msg.set_payload("This is the body of the email.")
    addresses = get_addresses_from_message(msg)
    assert addresses == [
        "recipient1@law-orga.de",
        "recipient2@law-orga.de",
        "recipient3@law-orga.de",
    ]


def test_mail_can_be_deleted(db):
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
    )
    mail.encrypt(user)
    content_file = ContentFile(content=b"abc", name="testing-mail-import")
    attachment = MailAttachment.create(
        mail_import=mail,
        filename="testing-mail-import",
        content=content_file,
        user=user,
    )
    mail.save()
    attachment.save()
    filename = attachment.content.name
    assert default_storage.exists(filename)
    delete_mail(user, mail.uuid)
    assert MailImport.objects.filter(uuid=mail.uuid).count() == 0
    assert MailAttachment.objects.filter(mail_import__uuid=mail.uuid).count() == 0
    assert not default_storage.exists(filename)
