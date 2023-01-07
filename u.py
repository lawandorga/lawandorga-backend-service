# from typing import Callable, Protocol, Type
#
# from pydantic import BaseModel
#
# from messagebus.domain.data import JsonDict
# from messagebus.impl.event import model_to_json
#
#
# class Number(Protocol):
#     number: int
#
#
# def double(number: Type[Number]):
#     return number.number * 2
#
#
# class Five:
#     number = 5
#
#
# double(Five)
#
#
# class EventData(Protocol):
#     def to_dict(self) -> JsonDict:
#         ...
#
#     @classmethod
#     def from_dict(cls, data: JsonDict) -> "EventData":
#         ...
#
#     @classmethod
#     def get_name(cls):
#         ...
#
#
# def handler(cls, on: Type[EventData] | list[Type[EventData]]):
#     return None
#
#
# class EventDataImpl(BaseModel):
#     def to_dict(self) -> JsonDict:
#         data = model_to_json(self)
#         return data
#
#     @classmethod
#     def from_dict(cls, data: JsonDict) -> BaseModel:
#         return cls(**data)
#
#     @classmethod
#     def get_name(cls):
#         return cls.__name__
#
#
# class Test(EventData):
#     number: int
#
#
# handler(None, Test)
