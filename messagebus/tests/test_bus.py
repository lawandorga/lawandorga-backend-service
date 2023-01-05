import pytest

from messagebus import MessageBus, RawEvent
from messagebus.domain.data import EventData


@MessageBus.event
class StuffHappened(EventData):
    happened: str


def test_bus_can_handle_events():
    # helper stuff
    called = False

    def change_state(e: RawEvent[StuffHappened]):
        nonlocal called
        called = True

    # check messagebus can handle events
    MessageBus.register_handler(StuffHappened, change_state)
    event = RawEvent(
        stream_name="stream", data=StuffHappened(happened="AbcHappened"), metadata={}
    )
    MessageBus.handle(event)

    assert called


def test_messagebus_does_not_call_the_wrong_handler():
    def change_state(e: RawEvent):
        assert False

    # check that the AbcHappened handler is not called
    MessageBus.register_handler("AbcHappened", change_state)
    event = RawEvent(
        stream_name="stream", data=StuffHappened(happened="XyzHappened"), metadata={}
    )
    MessageBus.handle(event)


def test_bus_can_work_with_multiple_handlers():
    # helper stuff
    called_1 = False
    called_2 = False

    def change_state_1(e: RawEvent):
        nonlocal called_1
        called_1 = True

    def change_state_2(e: RawEvent):
        nonlocal called_2
        called_2 = True

    # check messagebus can work with multiple handlers
    MessageBus.register_handler(StuffHappened, change_state_1)
    MessageBus.register_handler(StuffHappened, change_state_2)
    event = RawEvent(
        stream_name="stream", data=StuffHappened(happened="abcde"), metadata={}
    )
    MessageBus.handle(event)

    assert called_2 and called_1


def test_register_the_same_event_twice_error():
    class SomethingHappened(EventData):
        pass

    MessageBus.register_event_model(SomethingHappened)
    with pytest.raises(ValueError):
        MessageBus.register_event_model(SomethingHappened)


def test_get_event_model():
    class SthHappened(EventData):
        pass

    MessageBus.register_event_model(SthHappened)
    model = MessageBus.get_event_model(SthHappened.get_name())
    assert model == SthHappened
