import abc
from uuid import UUID

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.external import IOwner
from core.folders.domain.value_objects.tree import FolderTree
from core.seedwork.repository import Repository


class FolderRepository(Repository, abc.ABC):
    IDENTIFIER = "FOLDER"

    @classmethod
    def retrieve(cls, org_pk: int, uuid: UUID) -> Folder:
        raise NotImplementedError()

    @classmethod
    def get_or_create_records_folder(cls, org_pk: int, user: IOwner) -> Folder:
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
    def tree(cls, user: IOwner, org_pk: int) -> FolderTree:
        raise NotImplementedError()
