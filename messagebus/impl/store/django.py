from typing import Optional, Sequence

from django.db.models import Max

from messagebus.domain.message import DomainMessage, Message
from messagebus.domain.store import EventStore
from messagebus.impl.message import Message as DjangoMessage


class DjangoEventStore(EventStore):
    def append(
        self,
        stream_name: str,
        messages: Sequence[Message],
        position: Optional[int] = None,
    ):
        if len(messages) == 0:
            return

        messages_to_save: list[DjangoMessage] = []

        if position is None:
            messages_max = DjangoMessage.objects.filter(
                stream_name=stream_name
            ).aggregate(max_position=Max("position"))
            position = (
                messages_max["max_position"] + 1 if messages_max["max_position"] else 1
            )

        for message in messages:
            message_to_save = DjangoMessage(
                stream_name=stream_name,
                action=message.action,
                position=position,
                data=message.data,
                metadata=message.metadata,
            )
            messages_to_save.append(message_to_save)
            position += 1

        DjangoMessage.objects.bulk_create(messages_to_save)

    def load(self, stream_name: str) -> list[DomainMessage]:
        messages1 = DjangoMessage.objects.filter(stream_name=stream_name).order_by(
            "position"
        )
        messages2 = list(messages1)
        messages3: list[DomainMessage] = []
        for message1 in messages2:
            message2 = message1.to_domain_message()
            message2.add_to_metadata("position", message1.position)
            message2.add_to_metadata("time", message1.time)
            message2.add_to_metadata("stream_name", message1.stream_name)
            messages3.append(message2)
        return messages3
