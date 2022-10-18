from typing import TYPE_CHECKING, Type, Union

from apps.core.folders.domain.value_objects.encryption import (
    AsymmetricEncryption,
    SymmetricEncryption,
)

if TYPE_CHECKING:
    from apps.core.folders.domain.value_objects.key import AsymmetricKey, SymmetricKey


class Box(bytes):
    def __init__(
        self,
        encryption_class: Union[Type[AsymmetricEncryption], Type[SymmetricEncryption]],
    ):
        self._encryption_class = encryption_class
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
        self, key: Union["AsymmetricKey", "SymmetricKey"]
    ) -> Union[SymmetricEncryption, AsymmetricEncryption]:
        from apps.core.folders.domain.value_objects.key import (
            AsymmetricKey,
            SymmetricKey,
        )

        if isinstance(key, SymmetricKey) and issubclass(
            self._encryption_class, SymmetricEncryption
        ):
            return self._encryption_class(key=key.get_key())

        elif isinstance(key, AsymmetricKey) and issubclass(
            self._encryption_class, AsymmetricEncryption
        ):
            return self._encryption_class(
                private_key=key.get_decryption_key(),
                public_key=key.get_decryption_key(),
            )

        else:
            raise ValueError(
                "The key type '{}' does not match the encryption type '{}'".format(
                    key.KEY_TYPE, self._encryption_class.ENCRYPTION_TYPE
                )
            )


class LockedBox(Box):
    def __init__(
        self,
        enc_data: bytes,
        encryption_class: Union[Type[AsymmetricEncryption], Type[SymmetricEncryption]],
    ):
        self.__enc_data = enc_data
        super().__init__(encryption_class)

    def __repr__(self):
        return "LockedBox({}, {})".format(self.__enc_data, self._encryption_class)

    def unlock(self, key: Union["AsymmetricKey", "SymmetricKey"]) -> "OpenBox":
        encryption = self._get_encryption(key)
        data = encryption.decrypt(self.__enc_data)
        return OpenBox(data=data, encryption_class=self._encryption_class)

    @property
    def value(self) -> bytes:
        return self.__enc_data


class OpenBox(Box):
    def __init__(
        self,
        data: bytes,
        encryption_class: Union[Type[AsymmetricEncryption], Type[SymmetricEncryption]],
    ):
        self.__data = data
        super().__init__(encryption_class)

    def __repr__(self):
        return "OpenBox({}, {})".format(self.__data, self._encryption_class)

    def lock(self, key: Union["AsymmetricKey", "SymmetricKey"]) -> LockedBox:
        encryption = self._get_encryption(key)
        enc_data = encryption.encrypt(self.__data)
        return LockedBox(enc_data=enc_data, encryption_class=self._encryption_class)

    @property
    def value(self) -> bytes:
        return self.__data
