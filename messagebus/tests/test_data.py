from uuid import uuid4, UUID

from messagebus.domain.data import serialize, EventData


def test_serialize_uuid():
    uuid = uuid4()
    data_1 = {"id": uuid}
    data_2 = serialize(data_1)
    assert data_2['id'] == str(uuid)


class Driver(EventData):
    uuid: UUID


class Car(EventData):
    wheels: int
    doors = 2
    driver: Driver


def test_model_to_json_and_back():
    car_1 = Car(wheels=4, driver={'uuid': uuid4()})
    data = car_1.to_dict()
    car_2 = Car.from_dict(data)
    assert car_1 == car_2
    assert isinstance(data['driver']['uuid'], str)
