from typing import cast
from uuid import UUID

from core.auth.models import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.folder import FolderRepository
from core.seedwork.repository import RepositoryWarehouse
from core.seedwork.use_case_layer import use_case


def get_repository() -> FolderRepository:
    repository = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    return repository


@use_case()
def create_folder(__actor: RlcUser, name: str):
    folder = Folder.create(name=name, org_pk=__actor.org_id)
    folder.grant_access(to=__actor)
    r = get_repository()
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


@use_case()
def grant_access(__actor: RlcUser, to: RlcUser, folder_pk: UUID):
    r = get_repository()
    folder = r.retrieve(org_pk=__actor.org_id, pk=folder_pk)
    folder.grant_access(to=to, by=__actor)
    r.save(folder)


@use_case()
def revoke_access(__actor: RlcUser, of: RlcUser, folder_pk: UUID):
    r = get_repository()
    folder = r.retrieve(org_pk=__actor.org_id, pk=folder_pk)
    folder.revoke_access(of=of)
    r.save(folder)
