from typing import TYPE_CHECKING, Optional, Type, Union

from core.folders.domain.value_objects.encryption import (
    AsymmetricEncryption,
    SymmetricEncryption,
)

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

    def _get_encryption(
        self,
        key: Union["AsymmetricKey", "SymmetricKey"],
        encryption_class: Union[Type[AsymmetricEncryption], Type[SymmetricEncryption]],
    ) -> Union[SymmetricEncryption, AsymmetricEncryption]:
        from core.folders.domain.value_objects.key import AsymmetricKey, SymmetricKey

        if isinstance(key, SymmetricKey) and issubclass(
            encryption_class, SymmetricEncryption
        ):
            return encryption_class(key=key.get_key())

        elif isinstance(key, AsymmetricKey) and issubclass(
            encryption_class, AsymmetricEncryption
        ):
            return encryption_class(
                private_key=key.get_decryption_key(),
                public_key=key.get_encryption_key(),
            )

        else:
            raise ValueError(
                "The key type '{}' does not match the encryption type '{}'".format(
                    key.KEY_TYPE, encryption_class.ENCRYPTION_TYPE
                )
            )


class LockedBox(Box):
    def __init__(
        self,
        enc_data: bytes,
        encryption_class: Union[Type[AsymmetricEncryption], Type[SymmetricEncryption]],
    ):
        self.__enc_data = enc_data
        self.__encryption_class = encryption_class
        super().__init__()

    def __repr__(self):
        return "LockedBox({}, {})".format(self.__enc_data, self.__encryption_class)

    def unlock(self, key: Union["AsymmetricKey", "SymmetricKey"]) -> "OpenBox":
        encryption = self._get_encryption(key, self.__encryption_class)
        data = encryption.decrypt(self.__enc_data)
        return OpenBox(data=data)

    @property
    def value(self) -> bytes:
        return self.__enc_data


class OpenBox(Box):
    def __init__(
        self,
        data: bytes,
    ):
        self.__data = data
        self.__encryption_class: Optional[
            Union[Type[AsymmetricEncryption], Type[SymmetricEncryption]]
        ] = None
        super().__init__()

    def __repr__(self):
        return "OpenBox({})".format(self.__data)

    def lock(
        self,
        key: Union["AsymmetricKey", "SymmetricKey"],
        encryption_class: Union[Type[AsymmetricEncryption], Type[SymmetricEncryption]],
    ) -> LockedBox:
        encryption = self._get_encryption(key, encryption_class)
        enc_data = encryption.encrypt(self.__data)
        return LockedBox(enc_data=enc_data, encryption_class=encryption_class)

    @property
    def value(self) -> bytes:
        return self.__data
