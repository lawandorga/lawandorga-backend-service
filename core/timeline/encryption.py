from datetime import datetime
from typing import Optional

from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.symmetric_key import SymmetricKey
from messagebus import Event, MessageBus
from seedwork.types import JsonDict


class EncryptedEvent:
    @classmethod
    def create_from_event(
        cls, event: Event, key: SymmetricKey, fields: list[str]
    ) -> "EncryptedEvent":
        enc_event = EncryptedEvent(event)
        enc_event.encrypt(key, fields)
        return enc_event

    def __init__(self, event: Event):
        self._stream_name = event.stream_name
        self._action = event.action
        self._data = event.data
        self._metadata = event.metadata
        self._time = event.time
        self._position = event.position
        self._encrypted = False

    @property
    def stream_name(self) -> str:
        return self._stream_name

    @property
    def action(self) -> str:
        return self._action

    @property
    def time(self) -> Optional[datetime]:
        return self._time

    @property
    def data(self) -> JsonDict:
        return self._data

    @property
    def metadata(self) -> JsonDict:
        return self._metadata

    @property
    def position(self) -> Optional[int]:
        return self._position

    def set_position(self, position: int) -> None:
        self._position = position

    def set_time(self, time: datetime) -> None:
        self._time = time

    def encrypt(self, key: SymmetricKey, fields: list[str]):
        for field in fields:
            value = self._data[field]
            if not isinstance(value, str):
                raise ValueError(
                    f"Field {field} is not a string and can therefore not be encrypted."
                )
            box = OpenBox.create_from_str(value)
            self._data[field] = key.lock(box).as_dict()
        self._encrypted = True

    def decrypt(self, key: SymmetricKey, fields: list[str]):
        for field in fields:
            value = self._data[field]
            locked_box = LockedBox.create_from_dict(value)  # type: ignore
            box = key.unlock(locked_box)
            self._data[field] = box.value_as_str
        self._encrypted = False


def encrypt_events(events: list[Event], key: SymmetricKey, fields: list[str]) -> list[EncryptedEvent]:
    enc_events: list[EncryptedEvent] = []

    for e1 in events:
        enc_events.append(EncryptedEvent.create_from_event(e1, key, fields))

    return enc_events


def decrypt_events(events: list[EncryptedEvent], key: SymmetricKey, fields: list[str]) -> list[Event]:
    for e2 in events:
        e2.decrypt(key, fields)

    real_events = [MessageBus.get_event_from_message(e) for e in events]

    return real_events
