import abc
from typing import TYPE_CHECKING

from core.folders.domain.value_objects.keys import SymmetricKey

if TYPE_CHECKING:
    from core.folders.domain.aggregates.folder import Folder


class Item:
    name: str


class Upgrade:
    def __init__(self, folder: "Folder" = None):
        assert folder is not None
        self.__folder = folder
        self.__folder.add_upgrade(self)

    @property
    def folder(self) -> "Folder":
        return self.__folder

    @property
    @abc.abstractmethod
    def content(self) -> list[Item]:
        pass

    @abc.abstractmethod
    def reencrypt(self, old_key: SymmetricKey, new_key: SymmetricKey):
        pass
