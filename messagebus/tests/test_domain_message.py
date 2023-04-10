from datetime import datetime

from messagebus.domain.message import DomainMessage


def test_set_time_and_position():
    message = DomainMessage(stream_name="Test", action="action", data={"this": "that"})
    message.set_position(1)
    message.set_time(datetime(2020, 1, 1))
    assert message.position == 1
    assert message.time == datetime(2020, 1, 1)
