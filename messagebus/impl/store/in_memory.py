from typing import Optional, Sequence

from django.utils import timezone

from messagebus.domain.message import DomainMessage, Message
from messagebus.domain.store import EventStore


class InMemoryEventStore(EventStore):
    def __init__(self) -> None:
        super().__init__()
        if not hasattr(self, "_messages"):
            self._messages: dict[str, list[DomainMessage]] = {}

    def append(
        self,
        stream_name: str,
        messages: Sequence[Message],
        position: Optional[int] = None,
    ):
        if len(messages) == 0:
            return

        if position is None:
            position = 1
            if stream_name in self._messages and len(self._messages[stream_name]):
                last_message: DomainMessage = self._messages[stream_name][-1]
                if last_message.metadata["position"] is None:
                    raise ValueError("Last message has no position.")
                position = last_message.metadata["position"] + 1

        to_be_saved: list[DomainMessage] = []

        assert position is not None

        for event in messages:
            message = DomainMessage(
                action=event.action,
                data=event.data,
                metadata=event.metadata,
            )
            message.metadata["position"] = position
            message.metadata["time"] = timezone.now()
            message.metadata["stream_name"] = stream_name
            to_be_saved.append(message)
            position += 1

        if stream_name not in self._messages:
            self._messages[stream_name] = []

        self._messages[stream_name] += to_be_saved

    def load(self, stream_name: str) -> list[DomainMessage]:
        try:
            messages1 = self._messages[stream_name]
        except KeyError:
            return []
        messages2 = list(messages1)
        return messages2
