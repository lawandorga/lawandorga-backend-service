from core.folders.domain.aggregates.folder import Folder
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.folders.use_cases.folder import (
    grant_access_to_group,
    revoke_access_from_group,
)
from core.seedwork import test_helpers


def test_grant_access_to_group(db):
    org = test_helpers.create_org("Test Org")["org"]
    org_user = test_helpers.create_org_user(rlc=org)
    u = org_user["org_user"]

    folder = Folder.create(name="Test Folder", org_pk=u.org_id)
    folder.grant_access(u)

    r = DjangoFolderRepository()
    r.save(folder)

    group = test_helpers.create_group(u)["group"]
    folder.grant_access_to_group(group, u)
    assert len(folder.group_keys) == 1

    assert folder.has_access_group(group)
    r.save(folder)

    new_folder = r.retrieve(u.org_id, folder.uuid)
    assert new_folder.has_access_group(group), new_folder.keys

    new_folder.revoke_access_from_group(group)
    assert not new_folder.has_access_group(group)
    r.save(new_folder)

    new_folder = r.retrieve(u.org_id, folder.uuid)
    assert not new_folder.has_access_group(group)
    assert new_folder.has_access(u)


def test_grant_access_to_group_with_usecase(db):
    org = test_helpers.create_org("Test Org")["org"]
    org_user = test_helpers.create_org_user(rlc=org)
    u = org_user["org_user"]

    folder = Folder.create(name="Test Folder", org_pk=u.org_id)
    folder.grant_access(u)

    r = DjangoFolderRepository()
    r.save(folder)

    group = test_helpers.create_group(u)["group"]

    assert not folder.has_access_group(group)

    grant_access_to_group(u, group.uuid, folder.uuid)

    new_folder = r.retrieve(u.org_id, folder.uuid)
    assert new_folder.has_access_group(group)


def test_revoke_access_from_group(db):
    org = test_helpers.create_org("Test Org")["org"]
    org_user = test_helpers.create_org_user(rlc=org)
    u = org_user["org_user"]

    folder = Folder.create(name="Test Folder", org_pk=u.org_id)
    folder.grant_access(u)

    r = DjangoFolderRepository()
    r.save(folder)

    group = test_helpers.create_group(u)["group"]
    folder.grant_access_to_group(group, u)
    r.save(folder)

    assert folder.has_access_group(group)

    revoke_access_from_group(u, group.uuid, folder.uuid)

    new_folder = r.retrieve(u.org_id, folder.uuid)
    assert not new_folder.has_access_group(group)


def test_get_keys_with_group(db):
    org = test_helpers.create_org("Test Org")["org"]
    org_user_1 = test_helpers.create_org_user(rlc=org)
    u1 = org_user_1["org_user"]
    org_user_2 = test_helpers.create_org_user(email="tester@law-orga.de", rlc=org)
    u2 = org_user_2["org_user"]
    group = test_helpers.create_group(u1)["group"]
    group.add_member(u2, u1)
    folder = Folder.create(name="Test Folder", org_pk=u1.org_id)
    folder.grant_access(u1)
    folder.grant_access_to_group(group, u1)
    key1 = folder.get_decryption_key(u1)
    key2 = folder.get_decryption_key(u2)
    assert key1 == key2
