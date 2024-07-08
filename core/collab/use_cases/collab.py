from typing import Optional
from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.collab.models.collab import Collab
from core.collab.models.deprecated_collab_document import CollabDocument
from core.collab.models.deprecated_permission_for_collab_document import (
    PermissionForCollabDocument,
)
from core.collab.repositories.collab import CollabRepository
from core.collab.use_cases.footer import get_footer
from core.collab.use_cases.letterhead import get_letterhead
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.folder import FolderRepository
from core.folders.models import FOL_Folder
from core.permissions.static import (
    PERMISSION_COLLAB_READ_ALL_DOCUMENTS,
    PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS,
)
from core.rlc.models.org import Org
from core.seedwork.use_case_layer import UseCaseError, use_case


class TreeFolder:
    @classmethod
    def create(cls, org_pk: int, fr: FolderRepository) -> dict[str, "TreeFolder"]:
        tree: dict[str, "TreeFolder"] = {}
        folders = fr.get_list(org_pk)
        for f in folders:
            if f.parent_uuid is None:
                tree[f.name] = TreeFolder.create_single(f, folders)
        return tree

    @classmethod
    def create_single(cls, folder: Folder, folders: list[Folder]) -> "TreeFolder":
        children = {}
        for child in folders:
            if child.parent_uuid == folder.uuid:
                children[child.name] = cls.create_single(child, folders)
        return cls(folder, children)

    def __init__(self, folder: Folder, children: dict[str, "TreeFolder"]) -> None:
        self.folder = folder
        self.children = children


def create_folder(
    user: OrgUser,
    name: str,
    parent: Folder,
    fr: FolderRepository,
    org_pk: int,
    permissions: list[PermissionForCollabDocument],
    users_with_permission: list[OrgUser],
) -> TreeFolder:
    folder = Folder.create(name=name, org_pk=org_pk)
    folder.grant_access(user)
    folder.set_parent(parent, user)
    if parent.parent_uuid is None:
        folder.stop_inheritance()
    for p in permissions:
        if not folder.has_access_group(p.group_has_permission):
            folder.grant_access_to_group(group=p.group_has_permission, by=user)
    for u in users_with_permission:
        if not folder.has_access(u):
            folder.grant_access(u, user)
    fr.save(folder)
    return TreeFolder(folder=folder, children={})


def get_folder_from_path(
    user: OrgUser,
    path: list[str],
    tree: TreeFolder,
    fr: FolderRepository,
    permissions: list[PermissionForCollabDocument],
    users_with_permission: list[OrgUser],
) -> Folder:
    if len(path) == 0:
        return tree.folder
    if path[0] not in tree.children:
        assert isinstance(tree.folder.org_pk, int)
        folder = create_folder(
            user,
            path[0],
            tree.folder,
            fr,
            tree.folder.org_pk,
            permissions,
            users_with_permission,
        )
        return get_folder_from_path(
            user, path[1:], folder, fr, permissions, users_with_permission
        )
    return get_folder_from_path(
        user, path[1:], tree.children[path[0]], fr, permissions, users_with_permission
    )


def put_collab_doc_in_folder(
    user: OrgUser,
    collab_doc: CollabDocument,
    folder: Folder,
    aes_key_org: str,
    cr: CollabRepository,
):
    if collab_doc.versions.count() == 0:
        collab_doc.delete()
        return
    collab = Collab.create(user=user, title=collab_doc.name, folder=folder)
    text = collab_doc.versions.latest("created")
    text.decrypt(aes_key_rlc=aes_key_org)
    content = text.content
    assert isinstance(content, str)
    collab.sync(text=content, user=user)
    cr.save_document(collab, user, folder)


@use_case
def optimize(__actor: OrgUser, fr: FolderRepository, cr: CollabRepository):
    org = __actor.org
    if org.collab_migrated:
        return

    if not __actor.has_permission(
        PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS
    ) and not __actor.has_permission(PERMISSION_COLLAB_READ_ALL_DOCUMENTS):
        raise UseCaseError(
            "You need to have the permission to read or write "
            "all collab documents to migrate collab."
        )

    groups = set()
    for p in PermissionForCollabDocument.objects.filter(
        document__rlc_id=__actor.org_id
    ).select_related("group_has_permission"):
        groups.add(p.group_has_permission)

    for group in groups:
        if not group.has_member(__actor):
            raise UseCaseError(
                f"You need to be a member of group '{group.name}' to migrate collab."
            )

    if not FOL_Folder.objects.filter(
        org_id=__actor.org_id, name="Collab", _parent=None
    ).exists():
        folder = Folder.create(name="Collab", org_pk=__actor.org_id)
        folder.grant_access(__actor)
        for u in Org.objects.get(pk=__actor.org_id).users.exclude(pk=__actor.pk).all():
            folder.grant_access(u, __actor)
        fr.save(folder)

    aes_key_org = __actor.org.get_aes_key(
        user=__actor.user, private_key_user=__actor.get_private_key()
    )

    users_with_permission = []
    for user in list(Org.objects.get(pk=__actor.org_id).users.all()):
        has_p_1 = user.has_permission_as_user(PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS)
        has_p_2 = user.has_permission_as_user(PERMISSION_COLLAB_READ_ALL_DOCUMENTS)
        if has_p_1 or has_p_2:
            users_with_permission.append(user)

    for doc in list(CollabDocument.objects.filter(rlc_id=__actor.org_id)):
        tree = TreeFolder.create(__actor.org_id, fr)
        path = doc.path.split("/")
        tree_folder = tree["Collab"]
        folder = get_folder_from_path(
            __actor,
            path,
            tree_folder,
            fr,
            list(doc.collab_permissions.all()),
            users_with_permission,
        )
        put_collab_doc_in_folder(__actor, doc, folder, aes_key_org, cr)

    org.collab_migrated = True
    org.save()


@use_case
def create_collab(
    __actor: OrgUser,
    title: str,
    folder_uuid: UUID,
    cr: CollabRepository,
    fr: FolderRepository,
) -> Collab:
    folder = fr.retrieve(org_pk=__actor.org_id, uuid=folder_uuid)
    if not folder.has_access(__actor):
        raise UseCaseError(
            "You do not have access to this folder. Therefore you can not create a collab inside of it."
        )
    collab = Collab.create(user=__actor, title=title, folder=folder)
    cr.save_document(collab, __actor, folder)
    return collab


@use_case
def update_collab_title(
    __actor: OrgUser,
    collab_uuid: UUID,
    title: str,
    cr: CollabRepository,
    fr: FolderRepository,
) -> Collab:
    collab = cr.get_document(collab_uuid, __actor, fr)
    folder = fr.retrieve(org_pk=__actor.org_id, uuid=collab.folder_uuid)
    if not folder.has_access(__actor):
        raise UseCaseError(
            "You do not have access to this folder. Therefore you can not update this collab."
        )
    collab.update_title(title=title)
    cr.save_document(collab, __actor, folder)
    return collab


@use_case
def assign_template_to_collab(
    __actor: OrgUser,
    collab_uuid: UUID,
    letterhead_uuid: Optional[UUID],
    footer_uuid: Optional[UUID],
    cr: CollabRepository,
    fr: FolderRepository,
) -> Collab:
    collab = cr.get_document(collab_uuid, __actor, fr)
    folder = fr.retrieve(org_pk=__actor.org_id, uuid=collab.folder_uuid)
    if not folder.has_access(__actor):
        raise UseCaseError(
            "You do not have access to this folder. Therefore you can not update this collab."
        )
    if letterhead_uuid:
        letterhead = get_letterhead(__actor, letterhead_uuid)
        collab.update_letterhead(letterhead)
    else:
        collab.update_letterhead(None)

    if footer_uuid:
        footer = get_footer(__actor, footer_uuid)
        collab.update_footer(footer)
    else:
        collab.update_footer(None)

    cr.save_document(collab, __actor, folder)
    return collab


@use_case
def sync_collab(
    __actor: OrgUser,
    collab_uuid: UUID,
    text: str,
    cr: CollabRepository,
    fr: FolderRepository,
) -> Collab:
    collab = cr.get_document(collab_uuid, __actor, fr)
    folder = fr.retrieve(org_pk=__actor.org_id, uuid=collab.folder_uuid)
    if not folder.has_access(__actor):
        raise UseCaseError(
            "You do not have access to this folder. Therefore you can not sync this collab."
        )
    collab.sync(text=text, user=__actor)
    cr.save_document(collab, __actor, folder)
    return collab


@use_case
def delete_collab(__actor: OrgUser, collab_uuid: UUID, cr: CollabRepository):
    cr.delete_document(collab_uuid, __actor)
