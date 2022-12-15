from typing import cast

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.folder import FolderRepository
from core.seedwork import test_helpers
from core.seedwork.repository import RepositoryWarehouse


def test_key_invalidation_on_user_lock(db):
    org = test_helpers.create_org("Test Org")
    org_user = test_helpers.create_rlc_user(rlc=org)
    u = org_user["rlc_user"]

    folder = Folder.create(name="Test Folder", org_pk=u.org_id)
    folder.grant_access(u)

    r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    r.save(folder)

    u.lock()
    u.save()

    new_folder = r.retrieve(u.org_id, folder.uuid)

    assert u.locked
    assert new_folder.has_invalid_keys(u)
