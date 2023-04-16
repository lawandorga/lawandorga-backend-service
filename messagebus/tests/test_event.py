from messagebus import Event


class ObjectInWhichSomethingHappens:
    class SomethingHappened(Event):
        pass


def test_event_attributes():
    event = ObjectInWhichSomethingHappens.SomethingHappened()
    assert event.action == "SomethingHappened"
    assert event.aggregate_name == "ObjectInWhichSomethingHappens"
    assert event.metadata == {}
    assert str(event) == "SomethingHappened"
    assert event._name == "ObjectInWhichSomethingHappens.SomethingHappened"
