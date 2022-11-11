import abc
from typing import TYPE_CHECKING
from uuid import UUID

from core.seedwork.repository import Repository

if TYPE_CHECKING:
    from core.folders.domain.aggregates.upgrade import Upgrade


class UpgradeRepository(Repository, abc.ABC):
    @classmethod
    @abc.abstractmethod
    def load_upgrade(cls, pk: UUID) -> "Upgrade":
        pass
