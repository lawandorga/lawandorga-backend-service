import pytest

from core.folders.domain.aggregates.folder import Folder
from core.folders.tests.helpers.user import UserObject
from core.seedwork.domain_layer import DomainError


@pytest.fixture
def subfolder():
    user = UserObject()

    folder1 = Folder.create("Parent")
    folder1.grant_access(to=user)

    folder2 = Folder.create("Child")
    folder2.set_parent(folder1, user)

    yield folder2


def test_hierarchy(single_encryption):
    user = UserObject()

    folder1 = Folder.create("Parent")
    folder1.grant_access(to=user)

    folder2 = Folder.create("Child")
    folder2.set_parent(folder1, user)

    assert folder2.has_access(user)


def test_deep_hierarchy(single_encryption):
    user = UserObject()

    folders = []
    last_folder = Folder.create("1")
    last_folder.grant_access(user)

    for i in range(2, 100 + 1):
        folder = Folder.create(str(i))
        folder.set_parent(last_folder, user)
        folders.append(folder)
        last_folder = folder

    assert folders[-1].has_access(user)


def test_no_keys_error(single_encryption):
    folder1 = Folder.create("My Folder")
    with pytest.raises(AssertionError):
        folder1.get_encryption_key()
    with pytest.raises(AssertionError):
        folder1.get_decryption_key()


def test_hierarchy_no_access(single_encryption, subfolder):
    user = UserObject()
    with pytest.raises(DomainError):
        subfolder.get_decryption_key(requestor=user)


def test_parent_set(single_encryption, folder_user):
    folder1, user1 = folder_user
    user2 = UserObject()
    folder1.grant_access(user2, user1)

    folder2 = Folder.create("Second Folder")
    folder2.grant_access(user2)

    folder2.set_parent(folder1, user2)

    assert folder2.has_access(user1)


def test_inheritance_stop(single_encryption, folder_user):
    folder1, user1 = folder_user
    user2 = UserObject()
    folder2 = Folder.create("Test", folder1.org_pk, stop_inherit=True)
    folder2.grant_access(user1)
    folder2.set_parent(folder2, user1)
    folder1.grant_access(user2, user1)
    assert not folder2.has_access(user2)
    with pytest.raises(DomainError):
        folder2.get_decryption_key(requestor=user2)
