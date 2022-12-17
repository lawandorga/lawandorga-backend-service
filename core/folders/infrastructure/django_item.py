from core.folders.domain.aggregates.item import Item
from messagebus import DjangoAggregate


class DjangoItem(Item, DjangoAggregate):
    def set_name(self, name: str):
        self.add_event(
            "ItemRenamed",
            data={
                "uuid": self.uuid,
                "repository": self.REPOSITORY,
                "name": self.name,
                "folder_uuid": str(self.folder_uuid),
            },
        )
