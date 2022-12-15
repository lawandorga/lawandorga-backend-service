from typing import TYPE_CHECKING, Optional

from messagebus.domain.event import Event, JsonDict

if TYPE_CHECKING:
    from messagebus.impl.aggregate import DjangoAggregate
    from messagebus.impl.repository import Message


def create_event_from_message(message: "Message") -> "Event":
    return Event(message.stream_name, message.action, message.data, message.metadata)


def create_event_from_aggregate(
    aggregate: "DjangoAggregate",
    name: str,
    data: Optional[JsonDict] = None,
    metadata: Optional[JsonDict] = None,
) -> "Event":
    aggregate_name = aggregate.__class__.__name__
    aggregate_uuid = aggregate.uuid
    stream_name = "{}-{}".format(aggregate_name, aggregate_uuid)

    if data is None:
        data = {}

    if metadata is None:
        metadata = {}

    return Event(stream_name, name, data, metadata)
