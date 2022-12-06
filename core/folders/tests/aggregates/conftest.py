import pytest

from core.folders.domain.aggregates.content_upgrade import Content, ContentUpgrade
from core.folders.domain.aggregates.folder import Folder
from core.folders.tests.helpers.car import CarWithSecretName
from core.folders.tests.helpers.user import UserObject


@pytest.fixture
def car_content_key():
    car = CarWithSecretName(name="BMW")
    content = Content(
        "My Car",
        car,
    )
    key = content.encrypt()
    yield car, content, key


@pytest.fixture
def folder_upgrade_user(car_content_key):
    car, content, key = car_content_key
    user = UserObject()
    folder = Folder.create("New Folder")
    folder.grant_access(to=user)
    upgrade = ContentUpgrade(folder=folder)
    upgrade.add_content(content, key, user)
    yield folder, upgrade, user


@pytest.fixture
def folder_user(folder_upgrade_user):
    folder, upgrade, user = folder_upgrade_user
    yield folder, user


@pytest.fixture
def folder(folder_upgrade_user):
    folder, upgrade, user = folder_upgrade_user
    yield folder


@pytest.fixture
def upgrade_user(folder_upgrade_user):
    folder, upgrade, user = folder_upgrade_user
    yield upgrade, user
