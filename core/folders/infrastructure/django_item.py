from core.folders.domain.aggregates.item import Item
from messagebus import DjangoAggregate


class DjangoItem(Item, DjangoAggregate):
    def set_name(self, name: str):
        self.add_event(
            "ItemRenamed",
            data={
                "org_pk": self.org_pk,
                "uuid": str(self.uuid),
                "repository": self.REPOSITORY,
                "name": self.name,
                "folder_uuid": str(self.folder_uuid),
            },
        )

    def delete(self, *args, **kwargs):
        self.add_event(
            "ItemDeleted",
            data={
                "org_pk": self.org_pk,
                "uuid": str(self.uuid),
                "repository": self.REPOSITORY,
                "name": self.name,
                "folder_uuid": str(self.folder_uuid),
            },
        )
        return super().delete(*args, **kwargs)
