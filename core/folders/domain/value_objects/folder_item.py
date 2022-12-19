from typing import cast
from uuid import UUID

from core.folders.domain.aggregates.item import Item
from core.folders.domain.types import StrDict


class FolderItem:
    @staticmethod
    def create_from_item(item: Item):
        return FolderItem(
            name=item.name,
            repository=item.REPOSITORY,
            uuid=item.uuid,
            actions=item.actions,
        )

    @staticmethod
    def create_from_dict(d: StrDict):
        assert (
            "repository" in d
            and isinstance(d["repository"], str)
            and "uuid" in d
            and isinstance(d["uuid"], str)
            and "name" in d
            and isinstance(d["name"], str)
            and "actions" in d
            and isinstance(d["actions"], dict)
        )

        repository = d["repository"]
        name = d["name"]
        uuid = UUID(d["uuid"])
        actions = cast(dict[str, dict[str, str]], d["actions"])

        return FolderItem(name, uuid, repository, actions)

    def __init__(
        self, name: str, uuid: UUID, repository: str, actions: dict[str, dict[str, str]]
    ):
        assert isinstance(uuid, UUID)

        self.name = name
        self.uuid = uuid
        self.repository = repository
        self.actions = actions

    def as_dict(self) -> StrDict:
        return {
            "repository": self.repository,
            "uuid": str(self.uuid),
            "name": self.name,
            "actions": self.actions,  # type: ignore
        }

    def __repr__(self):
        return "FolderItem('{}', UUID('{}'), '{}', {})".format(
            self.name, self.uuid, self.repository, self.actions
        )
