from typing import Union
from uuid import UUID

from pydantic import BaseModel

JsonDict = dict[str, Union[str, bool, int, float, "JsonDict"]]


def serialize(data: dict) -> JsonDict:
    new_data: JsonDict = {}
    for key, item in data.items():
        assert isinstance(key, str)
        if isinstance(item, UUID):
            new_data[key] = str(item)
        elif isinstance(item, str) or isinstance(item, int) or isinstance(item, float) or isinstance(item, bool):
            new_data[key] = item
        elif isinstance(item, dict):
            new_data[key] = serialize(item)
        else:
            raise ValueError('unknown type in event data can not be put in data')
    return new_data


def model_to_json(model: BaseModel) -> JsonDict:
    return serialize(model.dict())


# def json_to_model(model_class: Type[BaseModel], data: JsonDict) -> BaseModel:
#     fields = {key: item.type_ for key, item in model_class.__fields__.items()}
#     new_data: dict = {}
#     for key, item in fields.items():
#         assert isinstance(key, str)
#         if item == UUID:
#             v = data[key]
#             assert isinstance(v, str)
#             new_data[key] = UUID(v)
#         elif item == str or item == int or item == float or item == bool:
#             new_data[key] = data[key]
#         elif issubclass(item, BaseModel):
#             v = data[key]
#             assert isinstance(v, dict)
#             new_data[key] = json_to_model(item, v)
#         else:
#             raise ValueError('unknown type in event data can not be put in data')
#     return model_class(**new_data)


class EventData(BaseModel):
    def to_dict(self) -> JsonDict:
        data = model_to_json(self)
        return data

    @classmethod
    def from_dict(cls, data: JsonDict) -> BaseModel:
        return cls(**data)
