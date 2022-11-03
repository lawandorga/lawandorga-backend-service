import abc
from typing import Dict


class Box(bytes):
    def __init__(self):
        super().__init__()

    def __new__(cls, **kwargs):

        value: bytes

        if issubclass(cls, OpenBox):
            value = kwargs["data"]
        elif issubclass(cls, LockedBox):
            value = kwargs["enc_data"]
        else:
            raise TypeError("The cls '{}' is of the wrong class.".format(cls))

        return super().__new__(cls, value)

    @property
    @abc.abstractmethod
    def value(self) -> bytes:
        pass


class LockedBox(Box):
    @staticmethod
    def create_from_dict(data: Dict[str, str]) -> "LockedBox":
        assert 'enc_data' in data and 'key_origin' in data

        enc_data = data['enc_data'].encode('utf-8')
        key_origin = data['key_origin']

        return LockedBox(enc_data, key_origin)

    def __init__(self, enc_data: bytes, key_origin: str):
        self.__enc_data = enc_data
        self.__key_origin = key_origin
        super().__init__()

    def __repr__(self):
        return "LockedBox({}, '{}')".format(self.__enc_data, self.__key_origin)

    def __dict__(self) -> Dict[str, str]:  # type: ignore
        return {
            'enc_data': self.__enc_data.decode('utf-8'),
            'key_origin': self.__key_origin
        }

    @property
    def key_origin(self) -> str:
        return self.__key_origin

    @property
    def value(self) -> bytes:
        return self.__enc_data


class OpenBox(Box):
    @staticmethod
    def create_from_dict(d: Dict[str, str]) -> "OpenBox":
        assert 'data' in d

        data = d['data'].encode('utf-8')

        return OpenBox(data)

    def __init__(self, data: bytes):
        self.__data = data
        super().__init__()

    def __repr__(self):
        return "OpenBox({})".format(self.__data)

    def __dict__(self):
        return {
            'data': self.__data.decode('utf-8')
        }

    @property
    def value(self) -> bytes:
        return self.__data
