import abc
from typing import Optional, Union

from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.encryption import (
    AsymmetricEncryption,
    SymmetricEncryption,
)


class Key(abc.ABC):
    def __init__(self, origin: Optional[str] = None):
        assert origin is not None

        self.__origin = origin

    def __eq__(self, other):
        if type(other) == type(self):
            return hash(other) == hash(self)
        return NotImplemented

    @property
    def origin(self):
        return self.__origin

    @abc.abstractmethod
    def get_encryption(self) -> Union[SymmetricEncryption, AsymmetricEncryption]:
        pass

    def lock(self, box: OpenBox) -> LockedBox:
        encryption = self.get_encryption()
        enc_data = encryption.encrypt(box.value)
        return LockedBox(enc_data=enc_data, key_origin=self.origin)

    def unlock(self, box: LockedBox) -> OpenBox:
        if self.origin != box.key_origin:
            raise ValueError(
                "This key can not unlock this box because the encryption versions do not match. '{}' != '{}'.".format(
                    self.origin, box.key_origin
                )
            )
        encryption = self.get_encryption()
        data = encryption.decrypt(box.value)
        return OpenBox(data=data)
