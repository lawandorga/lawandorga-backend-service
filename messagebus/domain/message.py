from datetime import datetime

from messagebus.domain.data import JsonDict


class Message:
    def __init__(
        self,
        stream_name: str,
        data: JsonDict,
        metadata: JsonDict,
        time: datetime,
        position: int,
        action: str,
    ):
        self.__stream_name = stream_name
        self.__data = data
        self.__metadata = metadata
        self.__action = action
        self.__position = position
        self.__time = time

    def __str__(self):
        return self.__action

    @property
    def action(self):
        return self.__action

    @property
    def name(self):
        return self.__action

    @property
    def position(self) -> int:
        return self.__position

    @property
    def _data(self) -> dict:
        return self.__data

    @property
    def metadata(self) -> dict:
        return self.__metadata

    @property
    def stream_name(self) -> str:
        return self.__stream_name

    @property
    def time(self) -> datetime:
        return self.__time
