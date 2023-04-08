from typing import Optional, cast
from uuid import UUID, uuid4

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.folder import FolderRepository
from core.seedwork.repository import RepositoryWarehouse
from core.timeline.utils import camel_to_snake_case
from messagebus import Event


class EventSourced:
    def __init__(self, events: list[Event]) -> None:
        for event in events:
            self.mutate(event)
        self.new_events: list[Event] = []

    def mutate(self, event: Event):
        action = camel_to_snake_case(event.action)
        func = getattr(self, f"when_{action}")
        func(event)

    def apply(self, event: Event):
        self.new_events.append(event)
        self.mutate(event)


class TimelineEvent(EventSourced):
    class Created(Event):
        text: str
        folder_uuid: UUID
        org_pk: int
        uuid: UUID = uuid4()

    @classmethod
    def create(cls, text: str, folder: Folder, org_pk: int):
        event = TimelineEvent()
        event.apply(
            TimelineEvent.Created(text=text, folder_uuid=folder.uuid, org_pk=org_pk)
        )
        event._folder = folder
        return event

    def __init__(self, events: list[Event] = []):
        super().__init__(events)
        self._folder: Optional[Folder] = None

    @property
    def folder(self) -> Folder:
        if self._folder is None:
            r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
            self._folder = r.retrieve(self.org_pk, self.folder_uuid)
        return self._folder

    def when_created(self, event: Created):
        self.text = event.text
        self.folder_uuid = event.folder_uuid
        self.uuid = event.uuid
        self.org_pk = event.org_pk

    def when_information_updated(self, text=None):
        if text is not None:
            self.text = text

    def when_deleted(self):
        pass
