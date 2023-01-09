from datetime import datetime
from typing import Generic, TypeVar

from messagebus.domain.data import EventData, JsonDict
from messagebus.domain.message import Message

D = TypeVar("D", bound=EventData)


class Event(Generic[D], Message):
    def __init__(
        self,
        stream_name: str,
        data: JsonDict,
        metadata: JsonDict,
        position: int,
        time: datetime,
        action: str,
    ):
        super().__init__(stream_name, data, metadata, time, position, action)

    @property
    def data(self) -> D:
        from messagebus import MessageBus

        model = MessageBus.get_event_model(self.action)
        data = model(**self._data)
        return data


class RawEvent(Generic[D]):
    def __init__(self, stream_name: str, data: D, metadata: JsonDict):
        self.__stream_name = stream_name
        self.__data = data
        self.__metadata = metadata

    def __str__(self):
        return self.name

    @property
    def data(self) -> D:
        return self.__data

    @property
    def name(self):
        return self.__data.__class__.__name__

    @property
    def metadata(self):
        return self.__metadata

    @property
    def stream_name(self):
        return self.__stream_name
