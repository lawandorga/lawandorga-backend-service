import abc

from apps.core.folders.domain.value_objects.symmetric_encryption import (
    SymmetricEncryption,
)

from .folder import Folder


class EncryptedItem(abc.ABC):
    content: "Content"

    @abc.abstractmethod
    def encrypt_content(self) -> SymmetricEncryption:
        pass

    @abc.abstractmethod
    def decrypt_content(self, encryption: SymmetricEncryption):
        pass


class Content(abc.ABC):
    def __init__(
        self,
        name: str,
        folder: Folder,
        encryption: SymmetricEncryption,
        item: EncryptedItem,
    ):
        self.__name = name
        self.__folder = folder
        self.__encryption = encryption
        self.__item = item

    def encrypt(self):
        self.__encryption = self.__item.encrypt_content()

    def decrypt(self, user: str, private_key_user: str):
        # private_key_folder = self.__folder.get_private_key(user, private_key_user)
        # enc_key = self.__item.get_enc_key()
        # TODO: decrypt enc_key with private key from folder
        # key = str(enc_key) + private_key_folder
        # TODO
        # self.__item.decrypt_content(key)
        pass
