from typing import TYPE_CHECKING, Optional
from uuid import UUID

if TYPE_CHECKING:
    from core.folders.domain.aggregates.folder import Item


class ItemRepository:
    IDENTIFIER: str

    def retrieve(self, uuid: UUID, org_pk: Optional[int] = None) -> "Item":
        raise NotImplementedError()

    def delete_items_of_folder(self, folder_uuid: UUID, org_pk: int | None) -> None:
        raise NotImplementedError()
