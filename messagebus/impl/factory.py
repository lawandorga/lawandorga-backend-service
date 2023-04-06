from typing import TYPE_CHECKING

from messagebus.domain.bus import MessageBus
from messagebus.domain.event import Event

if TYPE_CHECKING:
    from messagebus.impl.repository import Message


def create_event_from_message(message: "Message") -> Event:
    model = MessageBus.get_event_model(message._name)
    return model(
        **message.data,
        position=message.position,
        aggregate_uuid=message._aggregate_uuid,
        time=message.time
    )
