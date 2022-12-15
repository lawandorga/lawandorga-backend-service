from messagebus import Event, MessageBus


def test_bus_can_handle_events():
    # helper stuff
    data = {"happened": ""}

    def change_state(event: Event):
        event.data["happened"] = event.name

    # check messagebus can handle events
    MessageBus.register_handler("AbcHappened", change_state)
    event = Event(stream_name="stream", name="AbcHappened", data=data, metadata={})
    MessageBus.handle(event)

    assert data["happened"] == "AbcHappened"


def test_messagebus_does_not_call_the_wrong_handler():
    # helper stuff
    data = {"happened": ""}

    def change_state(event: Event):
        event.data["happened"] = event.name

    # check that the AbcHappened handler is not called
    MessageBus.register_handler("AbcHappened", change_state)
    event = Event(stream_name="stream", name="XyzHappened", data=data, metadata={})
    MessageBus.handle(event)

    assert data["happened"] == ""


def test_bus_can_work_with_multiple_handlers():
    # helper stuff
    data = {"happened_1": [], "happened_2": []}

    def change_state_1(event: Event):
        event.data["happened_1"].append(event.name)

    def change_state_2(event: Event):
        event.data["happened_2"].append(event.name)

    # check messagebus can work with multiple handlers
    event_name = "AbcHappened"
    MessageBus.register_handler(event_name, change_state_1)
    MessageBus.register_handler(event_name, change_state_2)
    event = Event(stream_name="stream", name="AbcHappened", data=data, metadata={})
    MessageBus.handle(event)

    assert [event_name] == data["happened_2"]
    assert [event_name] == data["happened_1"]
