from uuid import uuid4

from messagebus import Event


class ObjectInWhichSomethingHappens:
    class SomethingHappened(Event):
        pass


def test_event_attributes():
    uuid = uuid4()
    event = ObjectInWhichSomethingHappens.SomethingHappened()
    event.set_aggregate_uuid(uuid)
    assert event.action == "SomethingHappened"
    assert event.aggregate_name == "ObjectInWhichSomethingHappens"
    assert event.metadata == {}
    assert str(event) == "SomethingHappened"
    assert event._name == "ObjectInWhichSomethingHappens.SomethingHappened"
