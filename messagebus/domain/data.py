from typing import Union

# from uuid import UUID

# from pydantic import BaseModel

JsonDict = dict[str, Union[str, bool, int, float, "JsonDict"]]


# def serialize(data: dict) -> JsonDict:
#     new_data: JsonDict = {}
#     for key, item in data.items():
#         assert isinstance(key, str)
#         if isinstance(item, UUID):
#             new_data[key] = str(item)
#         elif (
#             isinstance(item, str)
#             or isinstance(item, int)
#             or isinstance(item, float)
#             or isinstance(item, bool)
#         ):
#             new_data[key] = item
#         elif isinstance(item, dict):
#             new_data[key] = serialize(item)
#         else:
#             raise ValueError("unknown type in event data can not be put in data")
#     return new_data


# def model_to_json(model: BaseModel) -> JsonDict:
#     return serialize(model.dict())


# class EventData(BaseModel):
#     def to_dict(self) -> JsonDict:
#         data = model_to_json(self)
#         return data

#     @classmethod
#     def from_dict(cls, data: JsonDict) -> BaseModel:
#         return cls(**data)

#     @classmethod
#     def get_name(cls):
#         return cls.__name__
