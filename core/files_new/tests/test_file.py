import pytest

from core.data_sheets.models import DataSheet, DataSheetEncryptionNew, DataSheetTemplate
from core.data_sheets.use_cases.access_delivery import (
    deliver_access_to_users_who_should_have_access,
)
from core.files_new.models import EncryptedRecordDocument
from core.files_new.use_cases.file import put_files_inside_of_folders
from core.seedwork.encryption import AESEncryption


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
    template = DataSheetTemplate.objects.create(name="test", rlc=user.org)
    record = DataSheet.objects.create(template=template)
    key = AESEncryption.generate_secure_key()
    enc = DataSheetEncryptionNew(record=record, user=user, key=key)
    enc.encrypt(user.get_public_key())
    enc.save()
    file = EncryptedRecordDocument.objects.create(
        name="test.txt", record=record, org=user.org, location="test"
    )
    assert file.folder_uuid is None and record.folder_uuid is None
    deliver_access_to_users_who_should_have_access(user)
    record = DataSheet.objects.get(pk=record.pk)
    file = EncryptedRecordDocument.objects.get(pk=file.pk)
    assert record.folder_uuid is not None and file.folder_uuid is None
    put_files_inside_of_folders(user)
    record = DataSheet.objects.get(pk=record.pk)
    file = EncryptedRecordDocument.objects.get(pk=file.pk)
    assert record.folder_uuid is not None and file.folder_uuid is not None
    assert file.folder.has_access(user)
    assert file.folder.folder == record.folder.folder
