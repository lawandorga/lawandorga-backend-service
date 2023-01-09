from messagebus import RawEvent
from messagebus.domain.data import EventData


class SomethingHappened(EventData):
    pass


def test_event_attributes():
    metadata = {"b": 2}
    event = RawEvent(stream_name="stream", data=SomethingHappened(), metadata=metadata)
    assert event.stream_name == "stream"
    assert event.name == "SomethingHappened"
    assert event.data == SomethingHappened()
    assert event.metadata == metadata
    assert str(event) == event.name
