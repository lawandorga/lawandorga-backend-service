import abc
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .folder import Folder


class Item:
    REPOSITORY: str
    uuid: Any
    folder_uuid: Optional[Any]
    name: Any
    actions: dict[str, dict[str, str]]

    def set_folder(self, folder: "Folder"):
        if self.folder_uuid is None:
            self.folder_uuid = folder.uuid
        assert folder.uuid == self.folder_uuid

    @abc.abstractmethod
    def set_name(self, name: str):
        """
        this method needs to set the name of an item and somehow inform the folder about the name change.
        no other method should be allowed to set the name of an item.
        """
        pass
