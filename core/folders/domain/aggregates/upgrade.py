import abc
from typing import TYPE_CHECKING
from uuid import UUID

from core.folders.domain.types import StrDict
from core.folders.domain.value_objects.keys import SymmetricKey

if TYPE_CHECKING:
    from core.folders.domain.aggregates.folder import Folder


class Item:
    name: str

    def __init__(self, name: str):
        self.name = name


class Upgrade:
    REPOSITORY: str
    pk: UUID

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
        return {"pk": str(self.pk), "repository": self.REPOSITORY}

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
