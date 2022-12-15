from typing import Generator

import pytest

from core.folders.domain.aggregates.folder import Folder
from core.folders.tests.helpers.user import UserObject


@pytest.fixture
def user_user_folders(
    single_encryption,
) -> Generator[tuple[UserObject, UserObject, list[Folder]], None, None]:
    user_1 = UserObject()
    user_2 = UserObject()

    folder_1 = Folder.create("New Folder")
    folder_1.grant_access(to=user_1)
    folder_1.grant_access(to=user_2, by=user_1)

    folder_2 = Folder.create("New Folder")
    folder_2.set_parent(folder_1, by=user_1)

    yield user_1, user_2, [folder_1, folder_2]


def test_grant_access(user_user_folders):
    user_1, user_2, folders = user_user_folders

    for folder in folders:
        folder.invalidate_keys_of(user_1)

    assert not folders[1].has_access(user_1) and not folders[0].has_access(user_1)


def test_fix_keys(user_user_folders):
    user_1, user_2, folders = user_user_folders

    for folder in folders:
        folder.invalidate_keys_of(user_1)

    user_2.fix_keys_of(user_1, folders)

    assert folders[1].has_access(user_1) and folders[0].has_access(user_1)


def test_check_invalid_keys(user_user_folders):
    user_1, user_2, folders = user_user_folders
    user_3 = UserObject()
    folders[1].grant_access(user_3, user_1)

    for folder in folders:
        folder.invalidate_keys_of(user_1)

    assert user_1.check_has_invalid_keys(folders)
    user_3.fix_keys_of(user_1, folders)
    assert user_1.check_has_invalid_keys(folders)
    user_2.fix_keys_of(user_1, folders)
    assert not user_1.check_has_invalid_keys(folders)


def test_fix_keys_error(user_user_folders):
    user_1, user_2, folders = user_user_folders

    with pytest.raises(ValueError):
        folders[0].fix_keys(user_2, user_1)
