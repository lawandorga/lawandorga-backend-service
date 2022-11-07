from typing import Optional, Union

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.aggregates.object import EncryptedObject
from core.folders.domain.aggregates.upgrade import Item, Upgrade
from core.folders.domain.external import IOwner
from core.folders.domain.value_objects.encryption import EncryptionPyramid
from core.folders.domain.value_objects.keys import EncryptedSymmetricKey, SymmetricKey
from core.seedwork.domain_layer import DomainError


class Content(Item):
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
    def item(self) -> EncryptedObject:
        return self.__item

    def encrypt(self) -> SymmetricKey:
        encryption_class = EncryptionPyramid.get_highest_symmetric_encryption()
        raw_key, version = encryption_class.generate_key()
        content_key = SymmetricKey.create(key=raw_key, origin=version)
        self.__item.encrypt(content_key)
        self.__encryption_version = encryption_class.VERSION
        return content_key

    def decrypt(self, key: SymmetricKey):
        assert self.__encryption_version is not None
        self.__item.decrypt(key, self.__encryption_version)


class ContentUpgrade(Upgrade):
    def __init__(
        self,
        folder: Folder = None,
        content: dict[str, tuple[Content, EncryptedSymmetricKey]] = None,
    ):
        self.__content = content if content is not None else {}

        super().__init__(folder=folder)

    @property
    def encryption_version(self) -> Optional[str]:
        if len(self.__content.items()) == 0:
            return None

        keys = map(lambda x: x[1], self.__content.values())

        versions = []
        for key in keys:
            versions.append(key.origin)

        if not all([v == versions[0] for v in versions]):
            raise Exception("Not all upgrade keys have the same encryption version.")

        return versions[0]

    def content(self) -> list[Item]:
        pass

    def reencrypt(self, old_folder_key: SymmetricKey, new_folder_key: SymmetricKey):
        new_content: dict[str, tuple[Content, EncryptedSymmetricKey]] = {}

        for name, item in self.__content.items():
            old_key = item[1].decrypt(old_folder_key)
            item[0].decrypt(old_key)
            new_key = item[0].encrypt()
            enc_new_key = EncryptedSymmetricKey.create(new_key, new_folder_key)
            new_content[name] = (item[0], enc_new_key)

        self.__content = new_content

    def __add_or_overwrite_content(
        self, content: Content, key: SymmetricKey, user: IOwner
    ):
        lock_key = self.folder.get_encryption_key(requestor=user)
        enc_key = EncryptedSymmetricKey.create(original=key, key=lock_key)
        self.__content[content.name] = (content, enc_key)
        # check
        self.folder.check_encryption_version(user)

    def add_content(self, content: Content, key: SymmetricKey, user: IOwner):
        if content.name in self.__content:
            raise DomainError(
                "This upgrade already contains an item with the same name."
            )
        self.__add_or_overwrite_content(content, key, user)

    def update_content(self, content: Content, key: SymmetricKey, user: IOwner):
        if content.name not in self.__content:
            raise DomainError("This upgrade does not contain an item with this name.")
        self.__add_or_overwrite_content(content, key, user)

    def delete_content(self, content: Content):
        if content.name not in self.__content:
            raise DomainError("This upgrade does not contain an item with this name.")

        del self.__content[content.name]

    def get_content_key(self, content: Content, user: IOwner):
        if content.name not in self.__content:
            raise DomainError("This upgrade does not contain the specified item.")

        unlock_key = self.folder.get_decryption_key(requestor=user)

        enc_key = self.__content[content.name][1]
        content_key = enc_key.decrypt(unlock_key)
        return content_key

    def get_content_by_name(self, name: str) -> Content:
        if name not in self.__content:
            raise DomainError("This upgrade does not contain the specified item.")
        return self.__content[name][0]
