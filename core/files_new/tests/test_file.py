import io
import sys

import pytest
from django.core.files.uploadedfile import UploadedFile

from core.files_new.models import EncryptedRecordDocument


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
