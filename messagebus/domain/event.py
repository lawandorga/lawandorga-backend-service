from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from messagebus.domain.data import JsonDict


class Event(BaseModel):
    aggregate_uuid: Optional[UUID] = None
    position: Optional[int] = None
    time: Optional[datetime] = None

    def __str__(self):
        return self.action

    @property
    def _name(self) -> str:
        return self.__class__.__qualname__

    @property
    def _qualname_splits(self) -> list[str]:
        splits = self._name.split(".")
        if len(splits) != 2:
            raise ValueError(f"Event {self._name} is not nested correctly. Make sure it inside a class.")
        return splits

    @property
    def action(self) -> str:
        return self._qualname_splits[1]

    # @property
    # def name(self) -> str:
    #     return self.action

    @property
    def aggregate_name(self) -> str:
        return self._qualname_splits[0]

    @property
    def stream_name(self) -> str:
        if self.aggregate_uuid is None:
            raise ValueError("Streamname can not be generated without aggregate_uuid.")
        return f"{self.aggregate_name}-{self.aggregate_uuid}"

    @property
    def data(self) -> JsonDict:
        return self._clean_data(self.dict())

    @property
    def metadata(self) -> JsonDict:
        return {}

    def set_aggregate_uuid(self, uuid: UUID) -> None:
        self.aggregate_uuid = uuid

    @classmethod
    def _get_name(cls) -> str:
        parts = cls.__qualname__.split(".")
        if len(parts) < 2:
            return "later"
        return f"{parts[-2]}.{parts[-1]}"

    @staticmethod
    def _clean_data(data: dict) -> JsonDict:
        new_data: JsonDict = {}
        for key, item in data.items():
            assert isinstance(key, str)
            if key == "aggregate_uuid":
                continue
            elif isinstance(item, UUID):
                new_data[key] = str(item)
            elif (
                isinstance(item, str)
                or isinstance(item, int)
                or isinstance(item, float)
                or isinstance(item, bool)
            ):
                new_data[key] = item
            elif isinstance(item, dict):
                new_data[key] = Event._clean_data(item)
            elif item is None:
                continue
            else:
                raise ValueError("unknown type in event data can not be put in data")
        return new_data


# D = TypeVar("D", bound=EventData)


# class Event(Generic[D], Message):
#     def __init__(
#         self,
#         stream_name: str,
#         data: JsonDict,
#         metadata: JsonDict,
#         position: int,
#         time: datetime,
#         action: str,
#     ):
#         super().__init__(stream_name, data, metadata, time, position, action)

#     @property
#     def data(self) -> D:
#         from messagebus import MessageBus

#         model = MessageBus.get_event_model(self.action)
#         data = model(**self._data)
#         return data


# class RawEvent(Generic[D]):
#     def __init__(self, stream_name: str, data: D, metadata: JsonDict):
#         self.__stream_name = stream_name
#         self.__data = data
#         self.__metadata = metadata

#     def __str__(self):
#         return self.name

#     @property
#     def data(self) -> D:
#         return self.__data

#     @property
#     def name(self):
#         return self.__data.__class__.__name__

#     @property
#     def metadata(self):
#         return self.__metadata

#     @property
#     def stream_name(self):
#         return self.__stream_name
