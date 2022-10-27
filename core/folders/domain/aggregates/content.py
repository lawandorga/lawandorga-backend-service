from typing import Union

from core.folders.domain.aggregates.object import EncryptedObject
from core.folders.domain.value_objects.encryption import EncryptionPyramid
from core.folders.domain.value_objects.keys import ContentKey


class Content:
    def __init__(
        self,
        name: str,
        item: EncryptedObject,
        symmetric_encryption_version: Union[str, None] = None,
    ):
        self.__name = name
        self.__item = item
        self.__encryption_version = symmetric_encryption_version

    @property
    def encryption_version(self):
        return self.__encryption_version

    @property
    def name(self):
        return self.__name

    @property
    def item(self):
        return self.__item

    def encrypt(self) -> ContentKey:
        encryption_class = EncryptionPyramid.get_highest_symmetric_encryption()
        raw_key, version = encryption_class.generate_key()
        content_key = ContentKey.create(key=raw_key, origin=version)
        self.__item.encrypt(content_key)
        self.__encryption_version = encryption_class.VERSION
        return content_key

    def decrypt(self, key: ContentKey):
        assert self.__encryption_version is not None
        self.__item.decrypt(key, self.__encryption_version)