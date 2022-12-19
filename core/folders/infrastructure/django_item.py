from core.folders.domain.aggregates.item import Item
from messagebus import DjangoAggregate


class DjangoItem(Item, DjangoAggregate):
    def set_name(self, name: str, org_pk: int):
        self.add_event(
            "ItemRenamed",
            data={
                "org_pk": org_pk,
                "uuid": str(self.uuid),
                "repository": self.REPOSITORY,
                "name": self.name,
                "folder_uuid": str(self.folder_uuid),
            },
        )
