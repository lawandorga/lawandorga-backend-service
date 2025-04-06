import io
import sys

import pytest
from django.core.files.uploadedfile import UploadedFile

from core.seedwork import test_helpers
from core.seedwork.domain_layer import DomainError
from core.upload.models.upload import UploadLink
from messagebus.domain.collector import EventCollector


@pytest.fixture
def org():
    yield test_helpers.create_raw_org()


@pytest.fixture
def user(org):
    yield test_helpers.create_raw_org_user(org=org)


@pytest.fixture
def link(org, user):
    folder = test_helpers.create_raw_folder(user=user)
    link = UploadLink.create(
        user=user, folder=folder, name="Big Files", collector=EventCollector()
    )
    yield link


@pytest.fixture
def file():
    text = "My Secret Document"
    bytes_io = io.BytesIO(bytes(text, "utf-8"))
    file = UploadedFile(
        bytes_io, "secret.txt", "text/plain", sys.getsizeof(bytes_io), None
    )
    yield file


def test_name_error(link, file, user):
    with pytest.raises(DomainError) as e:
        link.upload("MyFile3.pdf", file)
    assert "needs to end with" in str(e)
    with pytest.raises(DomainError) as e:
        link.upload("MyFile", file)
    assert "have an extension" in str(e)
    with pytest.raises(DomainError) as e:
        link.upload(".txt", file)
    assert "name and an extension" in str(e)


def test_filename_error(link, user):
    text = "My Secret Document"
    bytes_io = io.BytesIO(bytes(text, "utf-8"))
    file = UploadedFile(bytes_io, "secret", "text/plain", sys.getsizeof(bytes_io), None)
    with pytest.raises(DomainError) as e:
        link.upload("MyFile4.txt", file)
    assert "not correct" in str(e)


def test_upload_link_can_be_created():
    org = test_helpers.create_raw_org()
    user = test_helpers.create_raw_org_user(org=org)
    folder = test_helpers.create_raw_folder(user=user)
    UploadLink.create(
        user=user, folder=folder, name="Big Files", collector=EventCollector()
    )


def test_data_can_be_uploaded(link, file, user):
    file = link.upload("MyFile.txt", file)
    name, f = link.download(file.uuid, user)
    assert b"My Secret Document" in f.read() and name == "MyFile.txt"


def test_data_is_encrypted(link, file):
    file = link.upload("MyFile2.txt", file)
    f = file.file.file
    assert b"My Secret Document" not in f.read()


def test_link_can_be_disabled_and_upload_fails(link, file):
    link.disable()
    with pytest.raises(DomainError):
        link.upload("NewFile.txt", file)


def test_link_property(link):
    url = link.link
    link.disable()
    assert "" == link.link
    assert url != link.link
