from typing import Optional, Sequence

from django.utils import timezone

from messagebus.domain.message import DomainMessage, Message
from messagebus.domain.store import EventStore


class InMemoryEventStore(EventStore):
    def __init__(self) -> None:
        super().__init__()
        if not hasattr(self, "_messages"):
            self._messages: list[DomainMessage] = []

    def append(self, messages: Sequence[Message], position: Optional[int] = None):
        if len(messages) == 0:
            return

        if position is None:
            position = len(
                list(
                    filter(
                        lambda m: m.stream_name == messages[0].stream_name,
                        self._messages,
                    )
                )
            )

        to_be_saved: list[DomainMessage] = []

        for event in messages:
            position += 1
            message = DomainMessage(
                stream_name=event.stream_name,
                action=event.action,
                position=position,
                data=event.data,
                metadata=event.metadata,
                time=timezone.now(),
            )
            to_be_saved.append(message)

        self._messages += to_be_saved

    def load(self, stream_name: str) -> list[DomainMessage]:
        messages1 = filter(lambda m: m.stream_name == stream_name, self._messages)
        messages2 = list(messages1)
        return messages2
