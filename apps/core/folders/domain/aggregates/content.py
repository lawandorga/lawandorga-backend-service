import abc
from typing import Literal, Optional, Type

from apps.core.folders.domain.aggregates.folder import Folder
from apps.core.folders.domain.aggregates.object import EncryptedObject
from apps.core.folders.domain.value_objects.box import LockedBox
from apps.core.folders.domain.value_objects.encryption import SymmetricEncryption, AsymmetricEncryption
from apps.core.folders.domain.value_objects.key import ContentKey, FolderKey, AsymmetricKey


class Content:
    def __init__(
        self,
        name: str,
        # folder: Folder,
        # encryption: SymmetricEncryption,
        item: EncryptedObject,
        symmetric_encryption_hierarchy: dict[int, Type[SymmetricEncryption]],
        # asymmetric_encryption_hierarchy: dict[int, Type[AsymmetricEncryption]],
        symmetric_encryption_version: int = 0,
        # asymmetric_encryption_version: int = 0
    ):
        self.__name = name
        # self.__folder = folder
        # self.__encryption = encryption
        self._item = item
        self.__key: Optional[ContentKey] = None
        self.__symmetric_encryption_version = symmetric_encryption_version
        self.__symmetric_encryption_hierarchy = symmetric_encryption_hierarchy
        # self.__asymmetric_encryption_version = asymmetric_encryption_version
        # self.__asymmetric_encryption_hierarchy = asymmetric_encryption_hierarchy

    @property
    def key(self) -> ContentKey:
        assert self.__key is None or isinstance(self.__key.get_key(), LockedBox)
        return self.__key

    def get_symmetric_encryption_class(
        self, direction: Literal["ENCRYPTION", "DECRYPTION"]
    ) -> Type[SymmetricEncryption]:
        if direction == "DECRYPTION":
            return self.__symmetric_encryption_hierarchy[self.__symmetric_encryption_version]
        if direction == "ENCRYPTION":
            return self.__symmetric_encryption_hierarchy[max(self.__symmetric_encryption_hierarchy.keys())]
    #
    # def get_asymmetric_encryption_class(
    #     self, direction: Literal["ENCRYPTION", "DECRYPTION"]
    # ) -> Type[SymmetricEncryption]:
    #     if direction == "DECRYPTION":
    #         return self.__asymmetric_encryption_hierarchy[self.__asymmetric_encryption_version]
    #     if direction == "ENCRYPTION":
    #         return self.__asymmetric_encryption_hierarchy[max(self.__asymmetric_encryption_hierarchy.keys())]

    def encrypt(self, key: AsymmetricKey):

        # encrypt item
        encryption_class = self.get_symmetric_encryption_class("ENCRYPTION")
        raw_content_key = encryption_class.generate_key()
        content_key = ContentKey(key=raw_content_key, encryption_class=encryption_class)
        self._item.encrypt(key, encryption_class)
        self.__symmetric_encryption_version = max(self.__symmetric_encryption_hierarchy.keys())

        # encrypt key
        self.__key = content_key.encrypt(key)

    def decrypt(self, key: AsymmetricKey):

        # decrypt key
        key = self.__key.decrypt(folder_key)
        self.__key = None

        # decrypt item
        item_encryption_class = self.get_symmetric_encryption_class("DECRYPTION")
        self._item.decrypt(key, item_encryption_class)
