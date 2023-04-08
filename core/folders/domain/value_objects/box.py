import abc
import base64

from seedwork.types import JsonDict


class Box(bytes):
    def __new__(cls, *args, **kwargs):
        if issubclass(cls, OpenBox):
            value = kwargs["data"] if "data" in kwargs else args[0]
        elif issubclass(cls, LockedBox):
            value = kwargs["enc_data"] if "enc_data" in kwargs else args[0]
        else:
            raise TypeError("The cls '{}' is of the wrong class.".format(cls))

        return super().__new__(cls, value)

    def __eq__(self, other):
        if type(other) == type(self):
            return hash(other) == hash(self)
        return NotImplemented

    @property
    @abc.abstractmethod
    def value(self) -> bytes:
        pass


class LockedBox(Box):
    ENCODING = "ISO-8859-1"

    @staticmethod
    def to_str(data: bytes):
        data_1 = data
        data_2 = base64.b64encode(data_1)
        data_3 = data_2.decode(LockedBox.ENCODING)
        return data_3

    @staticmethod
    def to_bytes(data: str) -> bytes:
        data_1 = data
        data_2 = data_1.encode(LockedBox.ENCODING)
        data_3 = base64.b64decode(data_2)
        return data_3

    @staticmethod
    def create_from_dict(d: JsonDict) -> "LockedBox":
        assert (
            "enc_data" in d
            and "key_origin" in d
            and isinstance(d["enc_data"], str)
            and isinstance(d["key_origin"], str)
        )

        enc_data = LockedBox.to_bytes(d["enc_data"])
        key_origin: str = d["key_origin"]

        return LockedBox(enc_data=enc_data, key_origin=key_origin)

    def __init__(self, enc_data: bytes, key_origin: str):
        self.__enc_data = enc_data
        self.__key_origin = key_origin
        super().__init__()

    def __repr__(self):
        return "LockedBox({}, '{}')".format(self.__enc_data, self.__key_origin)

    def as_dict(self) -> JsonDict:
        return {
            "enc_data": LockedBox.to_str(self.__enc_data),
            "key_origin": self.__key_origin,
        }

    def __hash__(self):
        return hash("{}{}".format(self.__enc_data, self.__key_origin))

    @property
    def key_origin(self) -> str:
        return self.__key_origin

    @property
    def value(self) -> bytes:
        return self.__enc_data


class OpenBox(Box):
    @staticmethod
    def create_from_dict(d: JsonDict) -> "OpenBox":
        assert "data" in d and isinstance(d["data"], str)

        data = d["data"].encode("utf-8")

        return OpenBox(data=data)

    @staticmethod
    def create_from_str(data: str) -> "OpenBox":
        return OpenBox(data=data.encode("utf-8"))

    def __init__(self, data: bytes):
        self.__data = data
        super().__init__()

    def __repr__(self):
        return "OpenBox({})".format(self.__data)

    def as_dict(self) -> JsonDict:  # type: ignore
        return {"data": self.__data.decode("utf-8")}

    def __hash__(self):
        return hash("openbox{}".format(self.__data))

    def decode(self, *args, **kwargs):
        return self.__data.decode(*args, **kwargs)

    @property
    def value(self) -> bytes:
        return self.__data

    @property
    def value_as_str(self) -> str:
        return self.__data.decode("utf-8")
