import abc
from typing import TYPE_CHECKING, Any, Optional

from core.folders.domain.types import StrDict
from core.folders.domain.value_objects.symmetric_key import SymmetricKey

if TYPE_CHECKING:
    from core.folders.domain.aggregates.folder import Folder


class Item:
    name: str

    def __init__(self, name: str, actions: Optional[dict[str, str]] = None):
        self.name = name
        self.actions = actions if actions is not None else {}


class Upgrade:
    REPOSITORY: str
    uuid: Any

    # @classmethod
    # def create_from_dict(cls, d: StrDict, upgrade: "Upgrade") -> "Upgrade":
    #     assert (
    #         "pk" in d
    #         and isinstance(d["pk"], str)
    #         and "repository" in d
    #         and isinstance(d["repository"], str)
    #     )
    #
    #     assert d["pk"] == upgrade.pk
    #     assert d["repository"] == cls.REPOSITORY
    #
    #     return upgrade
    #
    # def __init__(self, folder: Optional["Folder"] = None, pk: Optional[UUID] = None):
    #     assert folder is not None and pk is not None
    #     self.__pk = pk
    #     self.__folder = folder

    def as_dict(self) -> StrDict:
        return {"uuid": str(self.uuid), "repository": self.REPOSITORY}

    @property
    @abc.abstractmethod
    def folder(self) -> "Folder":
        pass

    @property
    @abc.abstractmethod
    def content(self) -> list[Item]:
        pass

    @abc.abstractmethod
    def reencrypt(self, old_key: SymmetricKey, new_key: SymmetricKey):
        pass