from uuid import UUID

from core.folders.domain.aggregates.item import Item

from seedwork.types import JsonDict


class FolderItem:
    @staticmethod
    def create_from_item(item: Item):
        return FolderItem(
            name=item.name,
            repository=item.REPOSITORY,
            uuid=item.uuid,
        )

    @staticmethod
    def create_from_dict(d: JsonDict):
        assert (
            "repository" in d
            and isinstance(d["repository"], str)
            and "uuid" in d
            and isinstance(d["uuid"], str)
            and "name" in d
            and isinstance(d["name"], str)
        )

        repository = d["repository"]
        name = d["name"]
        uuid = UUID(d["uuid"])

        return FolderItem(name, uuid, repository)

    def __init__(self, name: str, uuid: UUID, repository: str):
        assert isinstance(uuid, UUID)

        self.name = name
        self.uuid = uuid
        self.repository = repository

    def as_dict(self) -> JsonDict:
        return {
            "repository": self.repository,
            "uuid": str(self.uuid),
            "name": self.name,
        }

    def __repr__(self):
        return "FolderItem('{}', UUID('{}'), '{}')".format(
            self.name, self.uuid, self.repository
        )
