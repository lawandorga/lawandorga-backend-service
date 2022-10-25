from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from core.folders.domain.value_objects.key import AsymmetricKey, SymmetricKey


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
    def value(self):
        return


class LockedBox(Box):
    def __init__(self, enc_data: bytes, encryption_version: str):
        self.__enc_data = enc_data
        self.__encryption_version = encryption_version
        super().__init__()

    def __repr__(self):
        return "LockedBox({}, {})".format(self.__enc_data, self.__encryption_version)

    def decrypt(self, key: Union["AsymmetricKey", "SymmetricKey"]) -> "OpenBox":
        if self.__encryption_version != key.encryption_version:
            raise ValueError(
                "This key can not unlock this box because the encryption versions do not match. '{}' != '{}'.".format(
                    self.__encryption_version, key.encryption_version
                )
            )
        encryption = key.get_encryption()
        data = encryption.decrypt(self.__enc_data)
        return OpenBox(data=data)

    @property
    def value(self) -> bytes:
        return self.__enc_data


class OpenBox(Box):
    def __init__(self, data: bytes):
        self.__data = data
        super().__init__()

    def __repr__(self):
        return "OpenBox({})".format(self.__data)

    def encrypt(self, key: Union["AsymmetricKey", "SymmetricKey"]) -> LockedBox:
        encryption = key.get_encryption()
        enc_data = encryption.encrypt(self.__data)
        return LockedBox(enc_data=enc_data, encryption_version=key.encryption_version)

    @property
    def value(self) -> bytes:
        return self.__data
