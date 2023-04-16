from typing import Any, Optional, Sequence

from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.symmetric_key import SymmetricKey
from messagebus import Event, MessageBus
from messagebus.domain.message import Message
from seedwork.types import JsonDict


class EncryptedEvent:
    @classmethod
    def create_from_event(cls, event: Event, encrypted=False) -> "EncryptedEvent":
        enc_event = EncryptedEvent(
            event.action,
            event.data,
            event.metadata,
        )
        enc_event._encrypted = encrypted
        return enc_event

    @classmethod
    def create_from_message(cls, message: Message, encrypted=False) -> "EncryptedEvent":
        enc_event = EncryptedEvent(
            message.action,
            message.data,
            message.metadata,
        )
        enc_event._encrypted = encrypted
        return enc_event

    def __init__(
        self,
        action: str,
        data: JsonDict,
        metadata: dict[str, Any],
    ):
        self._action = action
        self._data = data
        self._metadata = metadata
        self._encrypted = False

    @property
    def action(self) -> str:
        return self._action

    @property
    def data(self) -> JsonDict:
        return self._data

    @property
    def metadata(self) -> JsonDict:
        return self._metadata

    @property
    def stream_name(self) -> Optional[str]:
        return self._metadata.get("stream_name")

    def add_to_metadata(self, key: str, value: Any) -> None:
        self._metadata[key] = value

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


def encrypt(
    events: list[Event], key: SymmetricKey, fields: list[str]
) -> list[EncryptedEvent]:
    enc_events: list[EncryptedEvent] = []

    for e1 in events:
        enc_event = EncryptedEvent.create_from_event(e1)
        enc_event.encrypt(key, fields)
        enc_events.append(enc_event)

    return enc_events


def decrypt(
    aggregate_name: str,
    messages: Sequence[Message],
    key: SymmetricKey,
    fields: list[str],
) -> list[Event]:
    events: list[EncryptedEvent] = []
    for m1 in messages:
        enc_event = EncryptedEvent.create_from_message(m1, encrypted=True)
        enc_event.decrypt(key, fields)
        events.append(enc_event)

    real_events: list[Event] = []
    for e in events:
        real_event = MessageBus.get_event_from_message(aggregate_name, e)
        real_events.append(real_event)

    return real_events
