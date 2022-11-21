import abc
from typing import TYPE_CHECKING, Optional

from core.folders.domain.types import StrDict
from core.seedwork.repository import Repository

if TYPE_CHECKING:
    from core.folders.domain.aggregates.folder import Folder
    from core.folders.domain.aggregates.upgrade import Upgrade


class UpgradeRepository(Repository, abc.ABC):
    @classmethod
    @abc.abstractmethod
    def create_from_dict(
        cls, d: Optional[StrDict] = None, folder: Optional["Folder"] = None
    ) -> "Upgrade":
        pass
