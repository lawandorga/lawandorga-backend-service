import abc
from typing import Optional, Type, Union

from apps.core.folders.domain.value_objects.box import LockedBox, OpenBox
from apps.core.folders.domain.value_objects.encryption import (
    AsymmetricEncryption,
    SymmetricEncryption,
)
from apps.core.folders.domain.value_objects.key import AsymmetricKey, SymmetricKey


class EncryptedObject(abc.ABC):
    ENCRYPTED_FIELDS: list[str] = []

    @property
    def is_encrypted(self) -> Optional[bool]:

        is_encrypted = all(
            map(
                lambda f: isinstance(getattr(self, f, None), LockedBox),
                self.ENCRYPTED_FIELDS,
            )
        )
        if is_encrypted:
            return True

        is_not_encrypted = all(
            map(
                lambda f: isinstance(getattr(self, f, None), OpenBox),
                self.ENCRYPTED_FIELDS,
            )
        )
        if is_not_encrypted:
            return False

        return None

    def encrypt(
        self,
        key: Union[AsymmetricKey, SymmetricKey],
        encryption_class: Union[Type[SymmetricEncryption], Type[AsymmetricEncryption]],
    ):
        for field in self.ENCRYPTED_FIELDS:
            v = getattr(self, field, b"")

            if isinstance(v, LockedBox):
                raise ValueError("Field '{}' is already in a LockedBox.".format(field))

            v = OpenBox(
                data=v,
            )

            setattr(self, field, v.lock(key, encryption_class))

    def decrypt(
        self,
        key: Union[AsymmetricKey, SymmetricKey],
        encryption_class: Union[Type[SymmetricEncryption], Type[AsymmetricEncryption]],
    ):
        for field in self.ENCRYPTED_FIELDS:
            v = getattr(self, "{}".format(field), b"")

            if isinstance(v, OpenBox):
                raise ValueError("Field '{}' is already in a OpenBox.".format(field))

            v = LockedBox(
                enc_data=v,
                encryption_class=encryption_class,
            )

            setattr(self, field, v.unlock(key))
