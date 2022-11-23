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
    def retrieve(cls, org_pk: int, pk: UUID) -> Folder:
        pass

    @classmethod
    @abc.abstractmethod
    def dict(cls, org_pk: int) -> dict[UUID, Folder]:
        pass

    @classmethod
    @abc.abstractmethod
    def list(cls, org_pk: int) -> list[Folder]:
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
    def tree(cls, org_pk: int) -> FolderTree:
        pass

    @classmethod
    @abc.abstractmethod
    def find_key_owner(cls, slug: UUID) -> IOwner:
        pass
