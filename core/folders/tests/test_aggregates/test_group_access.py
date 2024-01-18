from core.folders.domain.aggregates.folder import Folder
from core.seedwork import test_helpers


def test_has_access_can_get_the_key(db):
    """
    There used to be a bug that has_access retured True but get_encryption_key raised
    an DomainError. This test ensures that this bug is fixed.
    """
    org = test_helpers.create_org("Test Org")["org"]
    org_user = test_helpers.create_org_user(rlc=org)
    u = org_user["rlc_user"]

    parentfolder = Folder.create(name="Parent Folder", org_pk=u.org_id)
    parentfolder.grant_access(u)

    folder = Folder.create(name="Test Folder", org_pk=u.org_id)
    folder.grant_access(u)
    folder.set_parent(parentfolder, u)

    subfolder = Folder.create(name="Subfolder", org_pk=u.org_id)
    subfolder.grant_access(u)
    subfolder.set_parent(folder, u)

    group = test_helpers.create_group(u)["group"]
    folder.grant_access_to_group(group, u)

    gu = test_helpers.create_org_user(rlc=org, email="tester@law-orga.de")["rlc_user"]
    group.add_member(gu, u)

    assert subfolder.has_access(gu) and subfolder.get_encryption_key(gu)
