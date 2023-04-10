from typing import Optional

from django.db.models import Max

from messagebus.domain.repository import M, MessageBusRepository
from messagebus.impl.message import Message


class DjangoMessageBusRepository(MessageBusRepository):
    @classmethod
    def save_message(cls, m: M, position: Optional[int] = None) -> M:
        if position is None:
            messages_max = Message.objects.filter(stream_name=m.stream_name).aggregate(
                max_position=Max("position")
            )
            position = (
                messages_max["max_position"] + 1 if messages_max["max_position"] else 1
            )

        message = Message(
            stream_name=m.stream_name,
            action=m.action,
            position=position,
            data=m.data,
            metadata=m.metadata,
        )
        message.save()

        m.set_position(message.position)
        m.set_time(message.time)

        return m
