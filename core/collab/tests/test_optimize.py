from core.auth.models.org_user import OrgUser
from core.collab.models.collab import Collab
from core.collab.models.collab_document import CollabDocument
from core.collab.models.collab_permission import CollabPermission
from core.collab.models.permission_for_collab_document import (
    PermissionForCollabDocument,
)
from core.collab.models.text_document_version import TextDocumentVersion
from core.collab.use_cases.collab import optimize
from core.folders.domain.aggregates.folder import Folder
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.folders.models import FoldersFolder
from core.permissions.static import PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS
from core.rlc.models.group import Group
from core.rlc.models.org import Org
from core.seedwork import test_helpers


def create_collab_document(org: Org, user: OrgUser, path="/Document"):
    aes_key_rlc = org.get_aes_key(
        user=user.user, private_key_user=user.get_private_key()
    )
    collab_document = CollabDocument.objects.create(rlc=org, path=path)
    version = TextDocumentVersion(
        document=collab_document, quill=False, content="Document Content"
    )
    version.encrypt(aes_key_rlc=aes_key_rlc)
    version.save()
    return collab_document


def create_collab_document_with_group_access(
    org: Org, user: OrgUser, group: Group, path="/Group"
):
    aes_key_rlc = org.get_aes_key(
        user=user.user, private_key_user=user.get_private_key()
    )
    collab_document = CollabDocument.objects.create(rlc=org, path=path)
    version = TextDocumentVersion(
        document=collab_document, quill=False, content="Document Group Content"
    )
    version.encrypt(aes_key_rlc=aes_key_rlc)
    version.save()
    permission = CollabPermission.objects.get(name="read_document")
    PermissionForCollabDocument.objects.create(
        permission=permission, document=collab_document, group_has_permission=group
    )
    assert collab_document.user_can_read(user.user)
    return collab_document


def find_folder(name, folders: list[Folder]):
    for folder in folders:
        if folder.name == name:
            return folder
    raise Exception("folder not found")


def test_optimize_works(db):
    u = test_helpers.create_org_user()
    user = u["rlc_user"]
    user.grant(PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS)

    u2 = test_helpers.create_org_user(email="dummy2@law-orga.de", rlc=user.org)
    no_access_user = u2["rlc_user"]

    u3 = test_helpers.create_org_user(email="tester@law-orga.de", rlc=user.org)
    group_user = u3["rlc_user"]

    u4 = test_helpers.create_org_user(email="dummy3@law-orga.de", rlc=user.org)
    has_p_user = u4["rlc_user"]
    has_p_user.grant(PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS)

    # test normal collab document
    create_collab_document(org=user.org, user=user)

    # test collab document with group access
    g = test_helpers.create_group(user=user)
    group = g["group"]
    group.add_member(group_user, user)
    create_collab_document_with_group_access(org=user.org, user=user, group=group)

    # test nested collab doc
    create_collab_document(org=user.org, user=user, path="/Document/SubDocument")

    # test nested collab doc with group access
    create_collab_document_with_group_access(
        org=user.org, user=user, group=group, path="/Document/SubDocument/GroupBottom"
    )

    # optimize
    optimize(user)

    # general assertions
    assert Collab.objects.count() == 4
    assert FoldersFolder.objects.filter(org_id=user.org_id, name="Collab").count() == 1
    assert Org.objects.get(pk=user.org_id).collab_migrated

    fr = DjangoFolderRepository()
    folders = fr.get_list(user.org_id)

    # assertions for normal collab document
    assert (
        FoldersFolder.objects.filter(org_id=user.org_id, name="Document").count() == 1
    )
    folder1 = find_folder("Document", folders)
    assert not folder1.has_access(no_access_user)
    assert not folder1.has_access(group_user)
    assert folder1.has_access(has_p_user)

    # assertions for collab document with group access
    assert FoldersFolder.objects.filter(org_id=user.org_id, name="Group").count() == 1
    folder2 = find_folder("Group", folders)
    assert folder2.has_access_group(group)
    assert not folder2.has_access(no_access_user)
    assert folder2.has_access(group_user)
    assert folder2.has_access(has_p_user)

    # assertions for nested collab doc
    assert (
        FoldersFolder.objects.filter(org_id=user.org_id, name="SubDocument").count()
        == 1
    )
    folder3 = find_folder("SubDocument", folders)
    assert not folder3.has_access(no_access_user)
    assert not folder3.has_access(group_user)
    assert folder3.parent == folder1
    assert folder3.has_access(user)
    assert folder3.has_access(has_p_user)

    # assertions for nested collab doc with group access
    assert (
        FoldersFolder.objects.filter(org_id=user.org_id, name="GroupBottom").count()
        == 1
    )
    folder4 = find_folder("GroupBottom", folders)
    assert folder4.has_access_group(group)
    assert not folder4.has_access(no_access_user)
    assert folder4.has_access(group_user)
    assert folder4.has_access(has_p_user)
