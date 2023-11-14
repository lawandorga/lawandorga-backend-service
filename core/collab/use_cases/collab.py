from uuid import UUID

from core.auth.models.org_user import RlcUser
from core.collab.models.collab import Collab
from core.collab.repositories.collab import CollabRepository
from core.folders.domain.repositories.folder import FolderRepository
from core.seedwork.use_case_layer import UseCaseError, use_case


@use_case
def create_collab(
    __actor: RlcUser,
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
def update_collab(
    __actor: RlcUser,
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
    collab.update(title=title)
    cr.save_document(collab, __actor, folder)
    return collab


@use_case
def sync_collab(
    __actor: RlcUser,
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
def delete_collab(__actor: RlcUser, collab_uuid: UUID, cr: CollabRepository):
    cr.delete_document(collab_uuid, __actor)
