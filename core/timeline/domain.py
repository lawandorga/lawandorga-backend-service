from datetime import datetime
from typing import Optional, cast
from uuid import UUID, uuid4

from pydantic import Field

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.folder import FolderRepository
from core.seedwork.eventsourcing import EventSourced
from core.seedwork.repository import RepositoryWarehouse
from messagebus import Event


class TimelineEvent(EventSourced):
    class Created(Event):
        text: str
        title: str = ""
        time: datetime = datetime(year=2023, month=1, day=1)
        folder_uuid: UUID
        org_pk: int
        uuid: UUID = Field(default_factory=uuid4)
        by: UUID

    class InformationUpdated(Event):
        uuid: UUID
        text: Optional[str] = None
        time: Optional[datetime] = None
        title: Optional[str] = None
        by: UUID

    class Deleted(Event):
        uuid: UUID
        by: UUID

    @classmethod
    def create(
        cls,
        title: str,
        text: str,
        time: datetime,
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
                text=text,
                folder_uuid=folder_uuid,
                org_pk=org_pk,
                by=by,
                time=time,
                title=title,
            )
        )

        if folder is not None:
            event._folder = folder

        return event

    def __init__(self, events: list[Event] = []):
        super().__init__(events)
        self._folder: Optional[Folder] = None

    @property
    def type(self) -> str:
        return "old"

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
        self.time = event.time
        self.title = event.title
        self.deleted = False

    def when_information_updated(self, event: InformationUpdated):
        if event.text is not None:
            self.text = event.text
        if event.time is not None:
            self.time = event.time
        if event.title is not None:
            self.title = event.title

    def when_deleted(self, event: Deleted):
        self.text = ""
        self.title = ""
        self.deleted = True
