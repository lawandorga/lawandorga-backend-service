from typing import Optional, cast
from uuid import UUID

from core.auth.models import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.use_cases.finders import folder_from_id, rlc_user_from_slug
from core.seedwork.repository import RepositoryWarehouse
from core.seedwork.use_case_layer import UseCaseError, find, use_case


def get_repository() -> FolderRepository:
    repository = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    return repository


@use_case()
def create_folder(__actor: RlcUser, name: str, parent: Optional[UUID]):
    r = get_repository()
    folder = Folder.create(name=name, org_pk=__actor.org_id)
    if parent:
        parent_folder = r.retrieve(__actor.org_id, parent)
        folder.set_parent(folder=parent_folder, by=__actor)
    else:
        folder.grant_access(to=__actor)
    r.save(folder)


@use_case
def rename_folder(__actor: RlcUser, name: str, folder=find(folder_from_id)):
    r = get_repository()
    folder.update_information(name=name)
    r.save(folder)


@use_case()
def update_folder(__actor: RlcUser, folder_pk: UUID, name: str):
    r = get_repository()
    folder = r.retrieve(org_pk=__actor.org_id, pk=folder_pk)
    folder.update_information(name=name)
    r.save(folder)


@use_case()
def delete_folder(__actor: RlcUser, folder_pk: UUID):
    r = get_repository()
    folder = r.retrieve(org_pk=__actor.org_id, pk=folder_pk)
    if folder.has_access(__actor):
        r.delete(folder)
    else:
        raise UseCaseError(
            "You can not delete this folder because you have no access to this folder."
        )


@use_case
def grant_access(
    __actor: RlcUser, to=find(rlc_user_from_slug), folder=find(folder_from_id)
):
    r = get_repository()
    folder.grant_access(to=to, by=__actor)
    r.save(folder)


@use_case
def revoke_access(
    __actor: RlcUser, of=find(rlc_user_from_slug), folder=find(folder_from_id)
):
    r = get_repository()
    folder.revoke_access(of=of)
    r.save(folder)
