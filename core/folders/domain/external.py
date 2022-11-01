import abc
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from core.folders.domain.value_objects.keys import AsymmetricKey


class IOwner(abc.ABC):
    slug: UUID

    @abc.abstractmethod
    def get_key(self, *args, **kwargs) -> "AsymmetricKey":
        pass
