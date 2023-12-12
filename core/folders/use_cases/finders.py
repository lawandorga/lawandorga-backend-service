from typing import cast
from uuid import UUID

from core.auth.models import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.aggregates.item import Item
from core.folders.domain.repositories.folder import FolderRepository
from core.folders.domain.repositories.item import ItemRepository
from core.rlc.models.group import Group
from core.seedwork.message_layer import MessageBusActor
from core.seedwork.repository import RepositoryWarehouse
from core.seedwork.use_case_layer import finder_function


@finder_function
def folder_from_uuid(actor: OrgUser | MessageBusActor, v: UUID) -> Folder:
    repository = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    org_id: int = actor.org_id  # type: ignore
    folder = repository.retrieve(org_pk=org_id, uuid=v)
    return folder


@finder_function
def rlc_user_from_uuid(actor: OrgUser, v: UUID) -> OrgUser:
    return OrgUser.objects.get(org__id=actor.org_id, uuid=v)


@finder_function
def item_from_repository_and_uuid(
    org_pk: int, repository_name: str, uuid: UUID
) -> Item:
    item_repository = cast(ItemRepository, RepositoryWarehouse.get(repository_name))
    item = item_repository.retrieve(uuid=uuid, org_pk=org_pk)
    return item


@finder_function
def group_from_uuid(actor: OrgUser, v: UUID) -> Group:
    return Group.objects.get(from_rlc__id=actor.org_id, uuid=v)
