from typing import cast
from uuid import UUID

from core.auth.models import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.aggregates.item import Item
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.domain.repositiories.item import ItemRepository
from core.seedwork.repository import RepositoryWarehouse
from core.seedwork.use_case_layer import finder_function


@finder_function
def folder_from_uuid(actor, v) -> Folder:
    repository = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    folder = repository.retrieve(org_pk=actor.org_id, uuid=v)
    return folder


@finder_function
def rlc_user_from_uuid(actor, v) -> RlcUser:
    return RlcUser.objects.get(org__id=actor.org_id, uuid=v)


@finder_function
def item_from_repository_and_uuid(
    org_pk: int, repository_name: str, uuid: UUID
) -> Item:
    item_repository = cast(ItemRepository, RepositoryWarehouse.get(repository_name))
    item = item_repository.retrieve(uuid=uuid, org_pk=org_pk)
    return item
