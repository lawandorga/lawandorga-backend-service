import abc
from uuid import UUID

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.external import IOwner
from core.folders.domain.value_objects.tree import FolderTree
from core.seedwork.repository import Repository


class FolderRepository(Repository, abc.ABC):
    IDENTIFIER = "FOLDER"

    @classmethod
    @abc.abstractmethod
    def retrieve(cls, org_pk: int, uuid: UUID) -> Folder:
        pass

    @classmethod
    @abc.abstractmethod
    def get_or_create_records_folder(cls, org_pk: int, user: IOwner) -> Folder:
        pass

    @classmethod
    @abc.abstractmethod
    def get_dict(cls, org_pk: int) -> dict[UUID, Folder]:
        pass

    @classmethod
    @abc.abstractmethod
    def get_list(cls, org_pk: int) -> list[Folder]:
        pass

    @classmethod
    @abc.abstractmethod
    def save(cls, folder: Folder):
        pass

    @classmethod
    @abc.abstractmethod
    def delete(cls, folder: Folder):
        pass

    @classmethod
    @abc.abstractmethod
    def tree(cls, user: IOwner, org_pk: int) -> FolderTree:
        pass
