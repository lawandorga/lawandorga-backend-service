from datetime import datetime

from messagebus.domain.message import DomainMessage


def test_set_time_and_position():
    message = DomainMessage(stream_name="Test", action="action", data={"this": "that"})
    message.add_to_metadata("position", 1)
    message.add_to_metadata("time", datetime(2020, 1, 1))
    assert message.metadata["position"] == 1
    assert message.metadata["time"] == datetime(2020, 1, 1)
