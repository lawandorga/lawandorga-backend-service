import pytest

from messagebus import Event, MessageBus


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
    MessageBus.register_handler(ObjectInWhichStuffHappens.StuffHappened, change_state)
    event = ObjectInWhichStuffHappens.StuffHappened(happened="AbcHappened")
    MessageBus.handle(event)

    assert called


def test_messagebus_does_not_call_the_wrong_handler():
    def change_state(e: ObjectInWhichStuffHappens.StuffHappened):
        assert False

    # check that the AbcHappened handler is not called
    MessageBus.register_handler(ObjectInWhichStuffHappens.NothingHappened, change_state)
    event = ObjectInWhichStuffHappens.StuffHappened(happened="XyzHappened")
    MessageBus.handle(event)


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
    MessageBus.register_handler(ObjectInWhichStuffHappens.StuffHappened, change_state_1)
    MessageBus.register_handler(ObjectInWhichStuffHappens.StuffHappened, change_state_2)
    event = ObjectInWhichStuffHappens.StuffHappened(happened="abcde")
    MessageBus.handle(event)

    assert called_2 and called_1


def test_get_event_model():
    model = MessageBus.get_event_model("ObjectInWhichStuffHappens.StuffHappened")
    assert model == ObjectInWhichStuffHappens.StuffHappened


def test_bus_run_checks_raises_error_on_nesting_error():
    class EventWithoutParent(Event):
        pass

    with pytest.raises(ValueError) as e:
        MessageBus.run_checks()

    assert "not nested correctly" in str(e.value)


def test_bus_run_checks_raises_error_on_duplicate():
    class Car:
        class Driven(Event):
            pass

    class Car:  # noqa: F811
        class Driven(Event):
            pass

    with pytest.raises(ValueError) as e:
        MessageBus._run_duplicate_check(Car.Driven)

    assert "defined more than once" in str(e.value)
