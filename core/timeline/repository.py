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

    def save(self, event: TimelineEvent, by: RlcUser) -> None:
        raise NotImplementedError()

    def load(self, uuid: UUID, by: RlcUser, folder: Folder) -> TimelineEvent:
        raise NotImplementedError()

    def list(self, folder: Folder, by: RlcUser) -> list[TimelineEvent]:
        raise NotImplementedError()


class EventStoreTimelineEventRepository(TimelineEventRepository):
    def __init__(self, event_store: EventStore) -> None:
        super().__init__()
        self._event_store = event_store

    def save(self, event: TimelineEvent, by: RlcUser) -> None:
        stream_name = f"TimelineEvent-{event.uuid}+{event.folder_uuid}"
        folder = event.folder
        key = folder.get_encryption_key(requestor=by)
        enc_events = encrypt(event.new_events, key, self.ENCRYPTED)
        self._event_store.append(stream_name, enc_events)

    def load(self, uuid: UUID, by: RlcUser, folder: Folder) -> TimelineEvent:
        stream_name = f"TimelineEvent-{uuid}+{folder.uuid}"

        messages = self._event_store.load(stream_name)

        if len(messages) == 0:
            raise ValueError(f"TimelineEvent with uuid {uuid} does not exist.")

        assert str(folder.uuid) == messages[0].data["folder_uuid"]
        key = folder.get_encryption_key(requestor=by)

        events = decrypt("TimelineEvent", messages, key, self.ENCRYPTED)

        event = TimelineEvent(events)

        return event

    def list(self, folder: Folder, by: RlcUser) -> list[TimelineEvent]:
        stream_name = f"TimelineEvent-%+{folder.uuid}"
        messages = self._event_store.load(stream_name)

        key = folder.get_encryption_key(requestor=by)

        events = decrypt("TimelineEvent", messages, key, self.ENCRYPTED)

        timeline_events: dict[UUID, TimelineEvent] = {}

        for event in events:
            if event.uuid not in timeline_events:
                timeline_events[event.uuid] = TimelineEvent([])
            timeline_events[event.uuid].mutate(event)

        return list(timeline_events.values())
