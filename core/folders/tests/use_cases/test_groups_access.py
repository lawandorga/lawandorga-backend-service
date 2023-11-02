from typing import cast

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.folder import FolderRepository
from core.folders.use_cases.folder import (
    grant_access_to_group,
    revoke_access_from_group,
)
from core.seedwork import test_helpers
from core.seedwork.repository import RepositoryWarehouse


def test_grant_access_to_group(db):
    org = test_helpers.create_org("Test Org")["org"]
    org_user = test_helpers.create_rlc_user(rlc=org)
    u = org_user["rlc_user"]

    folder = Folder.create(name="Test Folder", org_pk=u.org_id)
    folder.grant_access(u)

    r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    r.save(folder)

    group = test_helpers.create_group(u)["group"]
    folder.grant_access(group, u)
    assert len(folder.keys) == 2

    assert folder.has_access(group)
    r.save(folder)

    new_folder = r.retrieve(u.org_id, folder.uuid)
    assert new_folder.has_access(group), new_folder.keys

    new_folder.revoke_access(group)
    assert not new_folder.has_access(group)
    r.save(new_folder)

    new_folder = r.retrieve(u.org_id, folder.uuid)
    assert not new_folder.has_access(group)
    assert new_folder.has_access(u)


def test_grant_access_to_group_with_usecase(db):
    org = test_helpers.create_org("Test Org")["org"]
    org_user = test_helpers.create_rlc_user(rlc=org)
    u = org_user["rlc_user"]

    folder = Folder.create(name="Test Folder", org_pk=u.org_id)
    folder.grant_access(u)

    r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    r.save(folder)

    group = test_helpers.create_group(u)["group"]

    assert not folder.has_access(group)

    grant_access_to_group(u, group.uuid, folder.uuid)

    new_folder = r.retrieve(u.org_id, folder.uuid)
    assert new_folder.has_access(group)


def test_revoke_access_from_group(db):
    org = test_helpers.create_org("Test Org")["org"]
    org_user = test_helpers.create_rlc_user(rlc=org)
    u = org_user["rlc_user"]

    folder = Folder.create(name="Test Folder", org_pk=u.org_id)
    folder.grant_access(u)

    r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    r.save(folder)

    group = test_helpers.create_group(u)["group"]
    folder.grant_access(group, u)
    r.save(folder)

    assert folder.has_access(group)

    revoke_access_from_group(u, group.uuid, folder.uuid)

    new_folder = r.retrieve(u.org_id, folder.uuid)
    assert not new_folder.has_access(group)
