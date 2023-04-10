from messagebus.impl.message import Message as DjangoMessage


def test_string_method():
    message = DjangoMessage(stream_name="Test", action="action", data={"this": "that"})
    assert str(message) == "Test: {'this': 'that'}"
