import pytest

from core.data_sheets.models import DataSheet, DataSheetEncryptionNew, DataSheetTemplate
from core.data_sheets.use_cases.access_delivery import (
    deliver_access_to_users_who_should_have_access,
)
from core.files_new.models import EncryptedRecordDocument
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
