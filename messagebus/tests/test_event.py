from uuid import uuid4

from messagebus import Event


class ObjectInWhichSomethingHappens:
    class SomethingHappened(Event):
        pass


def test_event_attributes():
    event = ObjectInWhichSomethingHappens.SomethingHappened(uuid=uuid4())
    assert event.action == "SomethingHappened"
    assert event.aggregate_name == "ObjectInWhichSomethingHappens"
    assert event.metadata == {}
    assert event._name == "ObjectInWhichSomethingHappens.SomethingHappened"
