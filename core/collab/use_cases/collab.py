from typing import Optional
from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.collab.models.collab import Collab
from core.collab.repositories.collab import CollabRepository
from core.collab.use_cases.template import get_template
from core.data_sheets.use_cases.finders import find_record_from_folder_uuid
from core.folders.domain.repositories.folder import FolderRepository
from core.seedwork.use_case_layer import UseCaseError, use_case
from messagebus.domain.collector import EventCollector


def update_record_updated_at(__actor: OrgUser, folder_uuid: UUID):
    record = find_record_from_folder_uuid(__actor, folder_uuid)
    if not record:
        return
    record.update_timestamps()
    record.save()


@use_case
def create_collab(
    __actor: OrgUser,
    title: str,
    folder_uuid: UUID,
    cr: CollabRepository,
    fr: FolderRepository,
    collector: EventCollector,
) -> Collab:
    folder = fr.retrieve(org_pk=__actor.org_id, uuid=folder_uuid)
    if not folder.has_access(__actor):
        raise UseCaseError(
            "You do not have access to this folder. Therefore you can not create a collab inside of it."
        )
    collab = Collab.create(
        user=__actor, title=title, folder=folder, collector=collector
    )
    cr.save_document(collab, __actor, folder)
    update_record_updated_at(__actor, folder_uuid)
    return collab


@use_case
def update_collab_title(
    __actor: OrgUser,
    collab_uuid: UUID,
    title: str,
    cr: CollabRepository,
    fr: FolderRepository,
    collector: EventCollector,
) -> Collab:
    collab = cr.get_document(collab_uuid, __actor, fr)
    folder = fr.retrieve(org_pk=__actor.org_id, uuid=collab.folder_uuid)
    if not folder.has_access(__actor):
        raise UseCaseError(
            "You do not have access to this folder. Therefore you can not update this collab."
        )
    collab.update_title(title=title, collector=collector)
    cr.save_document(collab, __actor, folder)
    update_record_updated_at(__actor, collab.folder_uuid)
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
    update_record_updated_at(__actor, collab.folder_uuid)
    return collab


@use_case
def delete_collab(
    __actor: OrgUser,
    collab_uuid: UUID,
    cr: CollabRepository,
    fr: FolderRepository,
    collector: EventCollector,
):
    collab = cr.get_document(collab_uuid, __actor, fr)
    update_record_updated_at(__actor, collab.folder_uuid)
    cr.delete_document(collab_uuid, __actor, collector)
