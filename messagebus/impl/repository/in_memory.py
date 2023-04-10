from typing import Optional

from messagebus.domain.repository import M, MessageBusRepository
from messagebus.impl.message import Message


class InMemoryMessageBusRepository(MessageBusRepository):
    messages: list[Message] = []

    @classmethod
    def save_message(cls, m: M, position: Optional[int] = None) -> M:
        if not hasattr(cls, "messages"):
            cls.messages = []

        if position is None:
            position = 1
            for saved_message in cls.messages:
                if saved_message.stream_name == m.stream_name:
                    position += 1

        message: Message = Message(
            stream_name=m.stream_name,
            action=m.action,
            position=position,
            data=m.data,
            metadata=m.metadata,
        )
        cls.messages.append(message)

        m.set_position(message.position)
        m.set_time(message.time)

        return m
