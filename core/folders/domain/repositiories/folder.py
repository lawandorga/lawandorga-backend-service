import abc
from typing import TYPE_CHECKING
from uuid import UUID

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.value_objects.tree import FolderTree
from core.seedwork.repository import Repository

if TYPE_CHECKING:
    from core.auth.models.org_user import RlcUser


class FolderRepository(Repository, abc.ABC):
    IDENTIFIER = "FOLDER"

    @classmethod
    def retrieve(cls, org_pk: int, uuid: UUID) -> Folder:
        raise NotImplementedError()

    @classmethod
    def get_or_create_records_folder(cls, org_pk: int, user: "RlcUser") -> Folder:
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
    def delete(cls, folder: Folder):
        raise NotImplementedError()

    @classmethod
    def get_children(cls, org_pk: int, uuid: UUID) -> list[Folder]:
        raise NotImplementedError()

    @classmethod
    def tree(cls, user: "RlcUser", org_pk: int) -> FolderTree:
        raise NotImplementedError()
