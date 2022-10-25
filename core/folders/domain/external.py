import abc
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from core.folders.domain.value_objects.keys import AsymmetricKey


class IUser(abc.ABC):
    slug: UUID

    @abc.abstractmethod
    def get_key(self) -> "AsymmetricKey":
        pass
