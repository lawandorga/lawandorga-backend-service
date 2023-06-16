from uuid import UUID

from core.auth.models.org_user import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.timeline.domain import TimelineEvent
from core.timeline.encryption import decrypt, encrypt
from messagebus.domain.store import EventStore

from seedwork.repository import SingletonRepository


class TimelineEventRepository(SingletonRepository):
    IDENTIFIER = "TIMELINE_EVENT"
    ENCRYPTED = ["text", "title", "time"]
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
        stream_name = f"TimelineEvent-{event.folder_uuid}+{event.uuid}"
        folder = event.folder
        key = folder.get_encryption_key(requestor=by)
        enc_events = encrypt(event.new_events, key, self.ENCRYPTED)
        self._event_store.append(stream_name, enc_events)

    def load(self, uuid: UUID, by: RlcUser, folder: Folder) -> TimelineEvent:
        stream_name = f"TimelineEvent-{folder.uuid}+{uuid}"

        messages = self._event_store.load(stream_name)

        if len(messages) == 0:
            raise ValueError(f"TimelineEvent with uuid {uuid} does not exist.")

        assert str(folder.uuid) == messages[0].data["folder_uuid"]
        key = folder.get_encryption_key(requestor=by)

        events = decrypt("TimelineEvent", messages, key, self.ENCRYPTED)

        event = TimelineEvent(events)

        return event

    def list(self, folder: Folder, by: RlcUser) -> list[TimelineEvent]:
        stream_name = f"TimelineEvent-{folder.uuid}+"
        messages = self._event_store.load(stream_name, exact=False)

        key = folder.get_encryption_key(requestor=by)

        events = decrypt("TimelineEvent", messages, key, self.ENCRYPTED)

        timeline_events: dict[str, TimelineEvent] = {}

        for event in events:
            stream_name = event.metadata["stream_name"]
            if stream_name not in timeline_events:
                timeline_events[stream_name] = TimelineEvent([])
            timeline_events[stream_name].mutate(event)

        all_events = [e for e in timeline_events.values() if not e.deleted]
        sorted_events = list(sorted(all_events, key=lambda e: e.time))

        return sorted_events
