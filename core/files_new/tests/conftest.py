import io
import sys

import pytest
from django.core.files.uploadedfile import UploadedFile

from core.files_new.models import EncryptedRecordDocument
from core.tests import test_helpers
from messagebus.domain.collector import EventCollector


@pytest.fixture
def org():
    org = test_helpers.create_raw_org()
    yield org


@pytest.fixture
def user(org):
    user = test_helpers.create_raw_org_user(org)
    yield user


@pytest.fixture
def folder(user):
    folder = test_helpers.create_raw_folder(user)
    yield folder


@pytest.fixture
def file(user, folder):
    text = "My Secret Document"
    bytes_io = io.BytesIO(bytes(text, "utf-8"))
    f = UploadedFile(
        bytes_io, "secret.txt", "text/plain", sys.getsizeof(bytes_io), None
    )
    file = EncryptedRecordDocument.create(
        f, folder, user, upload=True, pk=1, collector=EventCollector()
    )
    yield file
