from typing import Optional
from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.collab.models.collab import Collab
from core.collab.repositories.collab import CollabRepository
from core.collab.use_cases.template import get_template
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.folder import FolderRepository
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
    template_uuid: Optional[UUID],
    cr: CollabRepository,
    fr: FolderRepository,
) -> Collab:
    collab = cr.get_document(collab_uuid, __actor, fr)
    folder = fr.retrieve(org_pk=__actor.org_id, uuid=collab.folder_uuid)
    if not folder.has_access(__actor):
        raise UseCaseError(
            "You do not have access to this folder. Therefore you can not update this collab."
        )
    if template_uuid:
        template = get_template(__actor, template_uuid)
        collab.update_template(template)
    else:
        collab.update_template(None)

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
