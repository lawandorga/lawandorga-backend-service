from messagebus import Event


def test_event_attributes():
    data = {"a": 1}
    metadata = {"b": 2}
    event = Event(
        stream_name="stream", name="AbcHappened", data=data, metadata=metadata
    )
    assert event.stream_name == "stream"
    assert event.name == "AbcHappened"
    assert event.data == data
    assert event.metadata == metadata
