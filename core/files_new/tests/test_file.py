import io
import sys

import pytest
from django.core.files.uploadedfile import UploadedFile

from core.files_new.models import EncryptedRecordDocument
from core.files_new.use_cases.file import put_files_inside_of_folders
from core.data_sheets.models import Record, RecordEncryptionNew, RecordTemplate
from core.data_sheets.use_cases.access_delivery import (
    deliver_access_to_users_who_should_have_access,
)
from core.seedwork.encryption import AESEncryption


@pytest.fixture
def file(user, folder):
    text = "My Secret Document"
    bytes_io = io.BytesIO(bytes(text, "utf-8"))
    f = UploadedFile(
        bytes_io, "secret.txt", "text/plain", sys.getsizeof(bytes_io), None
    )
    file = EncryptedRecordDocument.create(f, folder, user, upload=True, pk=1)
    yield file


def test_file_upload(file, user, folder):
    file.update_exists()
    assert file.exists
    file.delete_on_cloud()
    assert not file.exists
    file.update_exists()
    assert not file.exists


def test_key_regenerate_fails(file, user):
    with pytest.raises(AssertionError):
        file.generate_key(user)


def test_file_download(file, user):
    f = file.download(user)
    text = f.read()
    assert b"My Secret Document" in text


def test_put_inside_folders(db, user):
    user.user.save()
    user.org.save()
    user.save()
    template = RecordTemplate.objects.create(name="test", rlc=user.org)
    record = Record.objects.create(template=template)
    key = AESEncryption.generate_secure_key()
    enc = RecordEncryptionNew(record=record, user=user, key=key)
    enc.encrypt(user.get_public_key())
    enc.save()
    file = EncryptedRecordDocument.objects.create(
        name="test.txt", record=record, org=user.org, location="test"
    )
    assert file.folder_uuid is None and record.folder_uuid is None
    deliver_access_to_users_who_should_have_access(user)
    record = Record.objects.get(pk=record.pk)
    file = EncryptedRecordDocument.objects.get(pk=file.pk)
    assert record.folder_uuid is not None and file.folder_uuid is None
    put_files_inside_of_folders(user)
    record = Record.objects.get(pk=record.pk)
    file = EncryptedRecordDocument.objects.get(pk=file.pk)
    assert record.folder_uuid is not None and file.folder_uuid is not None
    assert file.folder.has_access(user)
    assert file.folder.folder == record.folder.folder
