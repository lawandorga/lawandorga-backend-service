from uuid import uuid4

import pytest

from messagebus import Event, MessageBus

bus = MessageBus()


class ObjectInWhichStuffHappens:
    class StuffHappened(Event):
        happened: str

    class NothingHappened(Event):
        pass


def test_bus_can_handle_events():
    # helper stuff
    called = False

    def change_state(e: ObjectInWhichStuffHappens.StuffHappened):
        nonlocal called
        called = True

    # check messagebus can handle events
    bus.register_handler(ObjectInWhichStuffHappens.StuffHappened, change_state)
    event = ObjectInWhichStuffHappens.StuffHappened(
        uuid=uuid4(), happened="AbcHappened"
    )
    bus.handle(event)

    assert called


def test_messagebus_does_not_call_the_wrong_handler():
    def change_state(e: ObjectInWhichStuffHappens.StuffHappened):
        assert False

    # check that the AbcHappened handler is not called
    bus.register_handler(ObjectInWhichStuffHappens.NothingHappened, change_state)
    event = ObjectInWhichStuffHappens.StuffHappened(
        uuid=uuid4(), happened="XyzHappened"
    )
    bus.handle(event)


def test_bus_can_work_with_multiple_handlers():
    # helper stuff
    called_1 = False
    called_2 = False

    def change_state_1(e: Event):
        nonlocal called_1
        called_1 = True

    def change_state_2(e: Event):
        nonlocal called_2
        called_2 = True

    # check messagebus can work with multiple handlers
    bus.register_handler(ObjectInWhichStuffHappens.StuffHappened, change_state_1)
    bus.register_handler(ObjectInWhichStuffHappens.StuffHappened, change_state_2)
    event = ObjectInWhichStuffHappens.StuffHappened(uuid=uuid4(), happened="abcde")
    bus.handle(event)

    assert called_2 and called_1


def test_bus_run_checks_raises_error_on_nesting_error():
    class EventWithoutParent(Event):
        pass

    with pytest.raises(ValueError) as e:
        bus.run_checks()

    assert "not nested correctly" in str(e.value)
