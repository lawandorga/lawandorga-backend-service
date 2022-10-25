import abc
from typing import Optional, Type, Union

from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.encryption import (
    AsymmetricEncryption,
    SymmetricEncryption,
)
from core.folders.domain.value_objects.key import AsymmetricKey, SymmetricKey


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
    ):
        for field in self.ENCRYPTED_FIELDS:
            v = getattr(self, field, b"")

            if isinstance(v, LockedBox):
                raise ValueError("Field '{}' is already in a LockedBox.".format(field))

            v = OpenBox(
                data=v,
            )

            setattr(self, field, key.lock(v))

    def decrypt(
        self,
        key: Union[AsymmetricKey, SymmetricKey],
        encryption_version: str,
    ):
        for field in self.ENCRYPTED_FIELDS:
            v = getattr(self, "{}".format(field), b"")

            if isinstance(v, OpenBox):
                raise ValueError("Field '{}' is already in a OpenBox.".format(field))

            v = LockedBox(
                enc_data=v,
                encryption_version=encryption_version,
            )

            setattr(self, field, key.unlock(v))
