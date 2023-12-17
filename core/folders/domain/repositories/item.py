import abc
from typing import TYPE_CHECKING, Optional
from uuid import UUID

if TYPE_CHECKING:
    from core.folders.domain.aggregates.folder import Item


class ItemRepository(abc.ABC):
    IDENTIFIER: str

    @classmethod
    @abc.abstractmethod
    def retrieve(cls, uuid: UUID, org_pk: Optional[int] = None) -> "Item":
        pass
