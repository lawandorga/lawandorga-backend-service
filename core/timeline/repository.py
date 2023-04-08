from typing import Optional
from uuid import UUID

from core.auth.models.org_user import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.seedwork.repository import Repository
from core.timeline.domain import TimelineEvent
from core.timeline.encryption import EncryptedEvent, decrypt_events, encrypt_events


class TimelineEventRepository(Repository):
    IDENTIFIER = "TIMELINE_EVENT"
    ENCRYPTED = ["text"]
    _instance: Optional["TimelineEventRepository"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TimelineEventRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()
        self._events: list[EncryptedEvent] = []

    def save(self, event: TimelineEvent, by: RlcUser):
        folder = event.folder
        key = folder.get_encryption_key(requestor=by)
        for e in event.new_events:
            e.set_aggregate_uuid(event.uuid)
        enc_events = encrypt_events(event.new_events, key, self.ENCRYPTED)
        self._events += enc_events

    def load(self, uuid: UUID, by: RlcUser, folder: Folder):
        relevant_events: list[EncryptedEvent] = []

        for e in self._events:
            if e.stream_name == f"TimelineEvent-{uuid}":
                relevant_events.append(e)

        if len(relevant_events) == 0:
            raise ValueError(f"TimelineEvent with uuid {uuid} does not exist.")

        assert str(folder.uuid) == relevant_events[0].data["folder_uuid"]
        key = folder.get_encryption_key(requestor=by)

        events = decrypt_events(relevant_events, key, self.ENCRYPTED)

        event = TimelineEvent(events)

        return event
