from uuid import UUID

from core.auth.models.org_user import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.timeline.domain import TimelineEvent
from core.timeline.encryption import decrypt, encrypt
from messagebus.domain.store import EventStore
from seedwork.repository import SingletonRepository


class TimelineEventRepository(SingletonRepository):
    IDENTIFIER = "TIMELINE_EVENT"
    ENCRYPTED = ["text"]
    SETTING = "REPOSITORY_TIMELINE_EVENT"
    CLASS = "TimelineEventRepository"

    def __init__(self, event_store: EventStore) -> None:
        super().__init__()
        self._event_store = event_store

    def save(self, event: TimelineEvent, by: RlcUser) -> None:
        raise NotImplementedError()

    def load(self, uuid: UUID, by: RlcUser, folder: Folder) -> TimelineEvent:
        raise NotImplementedError()


class InMemoryTimelineEventRepository(TimelineEventRepository):
    def save(self, event: TimelineEvent, by: RlcUser):
        folder = event.folder
        key = folder.get_encryption_key(requestor=by)
        for e in event.new_events:
            e.set_aggregate_uuid(event.uuid)
        enc_events = encrypt(event.new_events, key, self.ENCRYPTED)
        self._event_store.append(enc_events)

    def load(self, uuid: UUID, by: RlcUser, folder: Folder):
        messages = self._event_store.load(f"TimelineEvent-{uuid}")
        print(messages)

        if len(messages) == 0:
            raise ValueError(f"TimelineEvent with uuid {uuid} does not exist.")

        assert str(folder.uuid) == messages[0].data["folder_uuid"]
        key = folder.get_encryption_key(requestor=by)

        events = decrypt(messages, key, self.ENCRYPTED)

        event = TimelineEvent(events)

        return event


class DjangoTimelineEventRepository(TimelineEventRepository):
    def save(self, event: TimelineEvent, by: RlcUser):
        raise NotImplementedError()

    def load(self, uuid: UUID, by: RlcUser, folder: Folder) -> TimelineEvent:
        raise NotImplementedError()
