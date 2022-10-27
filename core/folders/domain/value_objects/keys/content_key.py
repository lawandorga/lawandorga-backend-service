from typing import Union

from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.keys.base import AsymmetricKey, SymmetricKey


class ContentKey(SymmetricKey):
    @staticmethod
    def create(key: str, origin: str) -> "ContentKey":
        return ContentKey(key=OpenBox(data=key.encode("utf-8")), origin=origin)

    def __init__(
        self,
        key: Union[OpenBox, LockedBox] = None,
        origin: Union[str, None] = None,
    ):
        assert origin is not None

        self._origin = origin
        self.__key = key

        super().__init__()

    def encrypt(self, lock_key: "AsymmetricKey") -> "ContentKey":
        assert isinstance(self.__key, OpenBox)

        enc_key = lock_key.lock(self.__key)
        return ContentKey(key=enc_key, origin=self.origin)

    def decrypt(self, unlock_key: "AsymmetricKey") -> "ContentKey":
        assert isinstance(self.__key, LockedBox)

        key = unlock_key.unlock(self.__key)
        return ContentKey(key=key, origin=self.origin)

    def get_key(self) -> str:
        assert isinstance(self.__key, OpenBox)
        key = self.__key.decode("utf-8")
        return key
