from typing import Optional
from uuid import UUID

from django.conf import settings
from django.utils.module_loading import import_string

from core.auth.models.org_user import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.seedwork.repository import Repository
from core.timeline.domain import TimelineEvent
from core.timeline.encryption import EncryptedEvent, decrypt_events, encrypt_events


class TimelineEventRepository(Repository):
    IDENTIFIER = "TIMELINE_EVENT"
    ENCRYPTED = ["text"]
    _instance: Optional["TimelineEventRepository"] = None
    SETTINGS = "REPOSITORY_TIMELINE_EVENT"

    def __new__(cls, *args, create=True, **kwargs):
        print(args, kwargs)

        if not create:
            return super().__new__(cls)

        module = import_string(settings.__getattr__(cls.SETTINGS))

        if cls._instance is None or not isinstance(cls._instance, module):
            cls._instance = module.__new__(module, *args, create=False, **kwargs)

        return cls._instance

    def __init__(self, event_store) -> None:
        super().__init__()
        self._event_store = event_store

    def save(self, event: TimelineEvent, by: RlcUser) -> None:
        raise NotImplementedError()

    def load(self, uuid: UUID, by: RlcUser, folder: Folder) -> TimelineEvent:
        raise NotImplementedError()


class InMemoryTimelineEventRepository(TimelineEventRepository):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
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


class DjangoTimelineEventRepository(TimelineEventRepository):
    def save(self, event: TimelineEvent, by: RlcUser):
        raise NotImplementedError()

    def load(self, uuid: UUID, by: RlcUser, folder: Folder) -> TimelineEvent:
        raise NotImplementedError()
