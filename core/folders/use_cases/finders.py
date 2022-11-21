from typing import cast

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.folder import FolderRepository
from core.seedwork.repository import RepositoryWarehouse


def folder_from_id(actor, v) -> Folder:
    repository = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    folder = repository.retrieve(org_pk=actor.org_id, pk=v)
    return folder
