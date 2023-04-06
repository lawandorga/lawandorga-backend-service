from uuid import UUID, uuid4

import pytest
from pydantic import BaseModel

from messagebus import Event


def test_serialize_uuid():
    # todo test event method
    uuid = uuid4()
    data_1 = {"id": uuid}
    data_2 = Event._clean_data(data_1)
    assert data_2["id"] == str(uuid)


class Driver(BaseModel):
    uuid: UUID


class Car(Event):
    wheels: int
    doors = 2
    driver: Driver


def test_model_to_json_and_back():
    car_1 = Car(wheels=4, driver={"uuid": uuid4()})
    data = car_1.data
    car_2 = Car(**data)
    assert car_1 == car_2
    assert isinstance(data["driver"]["uuid"], str)


def test_data_raises_error_on_unknown_data_type():
    data = {"working": 1, "not-working": str}
    with pytest.raises(ValueError):
        Event._clean_data(data)
