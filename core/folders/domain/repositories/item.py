from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    pass


class ItemRepository:
    IDENTIFIER: str

    def delete_items_of_folder(self, folder_uuid: UUID, org_pk: int) -> None:
        raise NotImplementedError()
