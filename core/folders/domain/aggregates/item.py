from typing import Any, Protocol
from uuid import UUID

from messagebus import EventData


class ItemAddedToFolder(EventData):
    org_pk: int
    uuid: UUID
    repository: str
    name: str
    folder_uuid: UUID


class ItemRenamed(EventData):
    org_pk: int
    uuid: UUID
    repository: str
    name: str
    folder_uuid: UUID


class ItemDeleted(EventData):
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
    def org_pk(self) -> int:
        ...

    def delete(self, *args, **kwargs):
        ...
