import abc
from typing import TYPE_CHECKING
from uuid import UUID

from core.seedwork.repository import Repository

if TYPE_CHECKING:
    from core.folders.domain.aggregates.folder import Item


class ItemRepository(Repository, abc.ABC):
    @classmethod
    @abc.abstractmethod
    def retrieve(cls, uuid: UUID) -> "Item":
        pass
