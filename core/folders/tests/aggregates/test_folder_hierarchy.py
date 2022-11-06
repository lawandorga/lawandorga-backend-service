import pytest

from core.folders.domain.aggregates.folder import Folder
from core.folders.tests.helpers.user import UserObject
from core.seedwork.domain_layer import DomainError


@pytest.fixture
def subfolder(car_content_key):
    car1, content1, key1 = car_content_key

    user = UserObject()

    folder1 = Folder.create("Parent")
    folder1.grant_access(to=user)

    folder2 = Folder.create("Child")
    folder2.set_parent(folder1, user)
    folder2.add_content(content1, key1, user)

    yield folder2


def test_hierarchy(single_encryption):
    user = UserObject()

    folder1 = Folder.create("Parent")
    folder1.grant_access(to=user)

    folder2 = Folder.create("Child")
    folder2.set_parent(folder1, user)

    assert folder2.has_access(user)


def test_deep_hierarchy(single_encryption, car_content_key):
    car1, content1, key1 = car_content_key

    user = UserObject()

    folders = []
    folder1 = Folder.create("1")
    folder1.grant_access(user)

    for i in range(2, 100 + 1):
        folder = Folder.create(str(i))
        folder.set_parent(folder1, user)
        folders.append(folder)

    folders[-1].add_content(content1, key1, user)

    content2 = folders[-1].get_content_by_name("My Car")
    key2 = folders[-1].get_content_key(content2, user)
    content2.decrypt(key2)
    car2 = content2.item

    assert car2.name == b"BMW"


def test_no_keys_error(single_encryption, car_content_key):
    folder1 = Folder.create("My Folder")
    with pytest.raises(DomainError):
        folder1.get_key()


def test_hierarchy_no_access(single_encryption, subfolder):
    user = UserObject()
    content = subfolder.get_content_by_name("My Car")
    with pytest.raises(DomainError):
        subfolder.get_content_key(content, user)
