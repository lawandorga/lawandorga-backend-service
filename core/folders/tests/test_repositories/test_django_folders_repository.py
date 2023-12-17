import pytest
from django.conf import settings

from core.auth.models import OrgUser, UserProfile
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.value_objects.encryption import EncryptionWarehouse
from core.folders.infrastructure.asymmetric_encryptions import AsymmetricEncryptionV1
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1
from core.rlc.models import Org


@pytest.fixture
def real_encryption(encryption_reset):
    EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionV1)
    EncryptionWarehouse.add_asymmetric_encryption(AsymmetricEncryptionV1)


@pytest.fixture
def repository(real_encryption):
    yield DjangoFolderRepository()


@pytest.fixture
def user(db):
    o = Org.objects.create(name="Test")
    p = UserProfile.objects.create(email="dummy@law-orga.de", name="Mr. Dummy")
    u = OrgUser(user=p, org=o)
    u.generate_keys(settings.DUMMY_USER_PASSWORD)
    u.save()
    o.generate_keys()
    user = OrgUser.objects.get(pk=u.pk)
    yield user


@pytest.fixture
def folder_uuid(db, user, repository):
    folder1 = Folder.create(name="New Folder", org_pk=user.org_id)
    folder1.grant_access(to=user)
    repository.save(folder1)
    yield folder1.uuid


def test_save(db, user, repository):
    folder1 = Folder.create(name="New Folder", org_pk=user.org_id)
    folder1.grant_access(to=user)
    repository.save(folder1)
    folder2 = repository.retrieve(user.org_id, folder1.uuid)
    assert folder2.has_access(user)


def test_retrieve(db, user, folder_uuid, repository):
    folder = repository.retrieve(user.org_id, folder_uuid)
    assert folder.has_access(user)


def test_list(db, user, repository, folder_uuid):
    folders = repository.get_list(user.org_id)
    assert folders[0].has_access(user)


def test_stop_inherit_saved(db, user, repository):
    folder1 = Folder.create(name="New Folder", org_pk=user.org_id, stop_inherit=True)
    folder1.grant_access(to=user)
    repository.save(folder1)
    folder2 = repository.retrieve(user.org_id, folder1.uuid)
    assert folder2.stop_inherit


def test_name_change_disable_saved(db, user, repository):
    folder1 = Folder.create(name="New Folder", org_pk=user.org_id, stop_inherit=True)
    folder1.restrict()
    repository.save(folder1)
    folder2 = repository.retrieve(user.org_id, folder1.uuid)
    assert folder2.restricted
