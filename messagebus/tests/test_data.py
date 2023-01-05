from uuid import UUID, uuid4

import pytest

from messagebus.domain.data import EventData, serialize


def test_serialize_uuid():
    uuid = uuid4()
    data_1 = {"id": uuid}
    data_2 = serialize(data_1)
    assert data_2["id"] == str(uuid)


class Driver(EventData):
    uuid: UUID


class Car(EventData):
    wheels: int
    doors = 2
    driver: Driver


def test_model_to_json_and_back():
    car_1 = Car(wheels=4, driver={"uuid": uuid4()})
    data = car_1.to_dict()
    car_2 = Car.from_dict(data)
    assert car_1 == car_2
    assert isinstance(data["driver"]["uuid"], str)


def test_data_raises_error_on_unknown_data_type():
    data = {'working': 1, 'not-working': str}
    with pytest.raises(ValueError):
        serialize(data)
