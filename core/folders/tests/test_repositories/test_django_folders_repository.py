import pytest
from django.conf import settings

from core.auth.models import OrgUser, UserProfile
from core.folders.domain.aggregates.folder import Folder
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.folders.models import FOL_ClosureTable, FOL_Folder
from core.rlc.models import Org


@pytest.fixture
def repository():
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


def disabled_test_closures_saved_and_deleted(db, user, repository):
    folder1 = Folder.create(name="New Folder", org_pk=user.org_id)
    folder1.grant_access(to=user)
    folder2 = Folder.create(name="New Folder", org_pk=user.org_id)
    folder2.grant_access(to=user)
    folder2.set_parent(folder1, user)

    repository.save(folder1)
    repository.save(folder2)

    f1 = FOL_Folder.objects.get(uuid=folder1.uuid)
    f2 = FOL_Folder.objects.get(uuid=folder2.uuid)
    assert FOL_ClosureTable.objects.filter(parent_id=f1.pk, child_id=f2.pk).exists()

    folder3 = Folder.create(name="New Folder", org_pk=user.org_id)
    folder3.grant_access(to=user)
    folder2.move(folder3, user)
    repository.save(folder3)
    repository.save(folder2)

    assert not FOL_ClosureTable.objects.filter(parent_id=f1.pk, child_id=f2.pk).exists()
