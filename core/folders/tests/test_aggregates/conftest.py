# type: ignore
import pytest

from core.folders.domain.aggregates.folder import Folder
from core.folders.tests.test_helpers.user import UserObject


@pytest.fixture
def folder_user():
    user = UserObject()
    folder = Folder.create("New Folder")
    folder.grant_access(to=user)
    yield folder, user


@pytest.fixture
def folder(folder_user):
    folder, user = folder_user
    yield folder
