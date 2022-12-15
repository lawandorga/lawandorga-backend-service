from typing import Union

JsonDict = dict[str, Union[str, bool, "JsonDict"]]


class Event:
    def __init__(self, stream_name: str, name: str, data: JsonDict, metadata: JsonDict):
        self.__stream_name = stream_name
        self.__name = name
        self.__data = data
        self.__metadata = metadata

    def __str__(self):
        return self.name

    @property
    def data(self):
        return self.__data

    @property
    def name(self):
        return self.__name

    @property
    def metadata(self):
        return self.__metadata

    @property
    def stream_name(self):
        return self.__stream_name
