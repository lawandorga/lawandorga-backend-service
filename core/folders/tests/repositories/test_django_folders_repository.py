import pytest

from core.auth.models import RlcUser, UserProfile
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.domain.value_objects.encryption import EncryptionWarehouse
from core.folders.infrastructure.asymmetric_encryptions import AsymmetricEncryptionV1
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1
from core.folders.tests.helpers.encryptions import (
    AsymmetricEncryptionTest1,
    SymmetricEncryptionTest1,
)
from core.rlc.models import Org
from core.seedwork.repository import RepositoryWarehouse


@pytest.fixture
def real_encryption(encryption_reset):
    EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionV1)
    EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionTest1)
    EncryptionWarehouse.add_asymmetric_encryption(AsymmetricEncryptionV1)
    EncryptionWarehouse.add_asymmetric_encryption(AsymmetricEncryptionTest1)


@pytest.fixture
def repository(real_encryption):
    RepositoryWarehouse.reset()
    RepositoryWarehouse.add_repository(DjangoFolderRepository)
    yield RepositoryWarehouse.get(FolderRepository)


@pytest.fixture
def user(db):
    o = Org.objects.create(name="Test")
    p = UserProfile.objects.create(email="dummy@law-orga.de", name="Mr. Dummy")
    u = RlcUser.objects.create(user=p, org=o)
    o.generate_keys()
    user = RlcUser.objects.get(pk=u.pk)
    yield user


def test_save(db, user, repository):
    folder1 = Folder.create("New Folder")
    folder1.grant_access(to=user)
    repository.save(folder1)
    folder2 = repository.retrieve(None, folder1.pk)
    assert folder2.has_access(user)


def test_retrieve(db):
    pass


def test_list(db):
    pass


def test_tree(db):
    pass


def test_find_key_owner(db):
    pass
