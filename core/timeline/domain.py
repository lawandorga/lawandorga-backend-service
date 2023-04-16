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
        by: UUID

    class InformationUpdated(Event):
        uuid: UUID
        text: Optional[str] = None
        by: UUID

    class Deleted(Event):
        uuid: UUID
        by: UUID

    @classmethod
    def create(
        cls,
        text: str,
        org_pk: int,
        by: UUID,
        folder: Optional[Folder] = None,
        folder_uuid: Optional[UUID] = None,
    ):
        assert folder is not None or folder_uuid is not None
        if folder is not None:
            folder_uuid = folder.uuid  # type: ignore
        assert folder_uuid is not None

        event = TimelineEvent()
        event.apply(
            TimelineEvent.Created(
                text=text, folder_uuid=folder_uuid, org_pk=org_pk, by=by
            )
        )

        if folder is not None:
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
        self.deleted = False

    def when_information_updated(self, event: InformationUpdated):
        if event.text is not None:
            self.text = event.text

    def when_deleted(self, event: Deleted):
        self.text = ""
        self.deleted = True
