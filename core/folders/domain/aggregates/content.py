from typing import Literal, Type

from core.folders.domain.aggregates.object import EncryptedObject
from core.folders.domain.value_objects.encryption import SymmetricEncryption
from core.folders.domain.value_objects.key import ContentKey


class Content:
    def __init__(
        self,
        name: str,
        item: EncryptedObject,
        symmetric_encryption_hierarchy: dict[int, Type[SymmetricEncryption]],
        symmetric_encryption_version: int = 0,
    ):
        self.__name = name
        self.__item = item
        self.__encryption_version = symmetric_encryption_version
        self.__encryption_hierarchy = symmetric_encryption_hierarchy

    @property
    def encryption_version(self):
        return self.__encryption_version

    @property
    def name(self):
        return self.__name

    @property
    def item(self):
        return self.__item

    def get_symmetric_encryption_class(
        self, direction: Literal["ENCRYPTION", "DECRYPTION"]
    ) -> Type[SymmetricEncryption]:
        if direction == "DECRYPTION":
            return self.__encryption_hierarchy[self.__encryption_version]
        if direction == "ENCRYPTION":
            return self.__encryption_hierarchy[max(self.__encryption_hierarchy.keys())]

    def encrypt(self) -> ContentKey:
        encryption_class = self.get_symmetric_encryption_class("ENCRYPTION")
        raw_key = encryption_class.generate_key()
        content_key = ContentKey(key=raw_key)
        self.__item.encrypt(content_key, encryption_class)
        self.__encryption_version = max(self.__encryption_hierarchy.keys())
        return content_key

    def decrypt(self, key: ContentKey):
        item_encryption_class = self.get_symmetric_encryption_class("DECRYPTION")
        self.__item.decrypt(key, item_encryption_class)
