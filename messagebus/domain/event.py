from typing import Generic, TypeVar

from messagebus.domain.data import EventData, JsonDict

D = TypeVar('D', bound=EventData)


class Event(Generic[D]):
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
