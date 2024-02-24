from typing import Any, Protocol
from uuid import UUID

from messagebus import Event


class FolderItem:
    class ItemAddedToFolder(Event):
        org_pk: int
        uuid: UUID
        repository: str
        name: str
        folder_uuid: UUID

    class ItemRenamed(Event):
        org_pk: int
        uuid: UUID
        repository: str
        name: str
        folder_uuid: UUID

    class ItemDeleted(Event):
        org_pk: int
        uuid: UUID
        repository: str
        name: str
        folder_uuid: UUID


class Item(Protocol):
    REPOSITORY: str
    uuid: Any
    folder_uuid: Any
    name: Any

    @property
    def org_pk(self) -> int: ...

    def delete(self, *args, **kwargs): ...
