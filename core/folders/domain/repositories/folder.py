import abc
from typing import TYPE_CHECKING
from uuid import UUID

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.item import ItemRepository

if TYPE_CHECKING:
    from core.auth.models.org_user import OrgUser


class FolderRepository(abc.ABC):
    IDENTIFIER = "FOLDER"

    @classmethod
    def retrieve(cls, org_pk: int, uuid: UUID) -> Folder:
        raise NotImplementedError()

    @classmethod
    def get_or_create_records_folder(cls, org_pk: int, user: "OrgUser") -> Folder:
        raise NotImplementedError()

    @classmethod
    def get_dict(cls, org_pk: int) -> dict[UUID, Folder]:
        raise NotImplementedError()

    @classmethod
    def get_list(cls, org_pk: int) -> list[Folder]:
        raise NotImplementedError()

    @classmethod
    def save(cls, folder: Folder):
        raise NotImplementedError()

    @classmethod
    def delete(cls, folder: Folder, repositories: dict[str, ItemRepository]):
        raise NotImplementedError()

    @classmethod
    def get_children(cls, org_pk: int, uuid: UUID) -> list[Folder]:
        raise NotImplementedError()
