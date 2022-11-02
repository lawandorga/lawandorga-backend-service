import abc


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
    def __init__(self, enc_data: bytes, encryption_version: str):
        self.__enc_data = enc_data
        self.__key_origin = encryption_version
        super().__init__()

    def __repr__(self):
        return "LockedBox({}, '{}')".format(self.__enc_data, self.__key_origin)

    @property
    def key_origin(self) -> str:
        return self.__key_origin

    @property
    def value(self) -> bytes:
        return self.__enc_data


class OpenBox(Box):
    def __init__(self, data: bytes):
        self.__data = data
        super().__init__()

    def __repr__(self):
        return "OpenBox({})".format(self.__data)

    @property
    def value(self) -> bytes:
        return self.__data
