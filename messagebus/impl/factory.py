from typing import TYPE_CHECKING, Optional

from messagebus.domain.data import EventData
from messagebus.domain.event import Event, JsonDict, RawEvent
from messagebus.impl.object import Object

if TYPE_CHECKING:
    from messagebus.impl.repository import Message


def create_event_from_message(message: "Message") -> Event:
    return Event(
        stream_name=message.stream_name,
        data=message.data,
        metadata=message.metadata,
        action=message.action,
        position=message.position,
        time=message.time,
    )


def create_event_from_aggregate(
    aggregate: Object,
    data: EventData,
    metadata: Optional[JsonDict] = None,
) -> "RawEvent":
    aggregate_name = aggregate.__class__.__name__
    aggregate_uuid = aggregate.uuid
    stream_name = "{}-{}".format(aggregate_name, aggregate_uuid)

    if metadata is None:
        metadata = {}

    return RawEvent(stream_name, data, metadata)
