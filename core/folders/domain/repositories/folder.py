from typing import TYPE_CHECKING
from uuid import UUID

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.item import ItemRepository

if TYPE_CHECKING:
    from core.auth.models.org_user import OrgUser


class FolderRepository:
    IDENTIFIER = "FOLDER"

    def retrieve(self, org_pk: int, uuid: UUID) -> Folder:
        raise NotImplementedError()

    def get_or_create_records_folder(self, org_pk: int, user: "OrgUser") -> Folder:
        raise NotImplementedError()

    def get_dict(self, org_pk: int) -> dict[UUID, Folder]:
        raise NotImplementedError()

    def get_list(self, org_pk: int) -> list[Folder]:
        raise NotImplementedError()

    def save(self, folder: Folder):
        raise NotImplementedError()

    def delete(self, folder: Folder, repositories: list[ItemRepository]):
        raise NotImplementedError()

    def get_children(self, org_pk: int, uuid: UUID) -> list[Folder]:
        raise NotImplementedError()

    def get_root_folders(self, org_pk: int) -> list[Folder]:
        raise NotImplementedError()

    def get_parent_folders(self, org_pk: int, uuid: UUID) -> list[Folder]:
        raise NotImplementedError()
