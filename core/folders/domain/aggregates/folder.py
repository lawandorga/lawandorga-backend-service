from typing import Dict, List, Literal, Tuple, Type
from uuid import UUID

from core.folders.domain.aggregates.content import Content
from core.folders.domain.value_objects.encryption import AsymmetricEncryption
from core.folders.domain.value_objects.key import ContentKey, FolderKey
from core.seedwork.domain_layer import DomainError


class Folder:
    def __init__(
        self,
        name: str = None,
        # parent: Optional["Folder"],
        asymmetric_encryption_hierarchy: dict[int, Type[AsymmetricEncryption]] = None,
        encryption_version: int = 0,
        pk: UUID = None,
        keys: List[FolderKey] = None,
        content: Dict[str, Tuple[Content, ContentKey]] = None,
    ):
        assert name and asymmetric_encryption_hierarchy

        self.__pk = pk
        self.__name = name
        # self.__parent = parent
        self.__content = content if content is not None else {}
        self.__keys = keys if keys is not None else []
        self.__encryption_hierarchy = asymmetric_encryption_hierarchy
        self.__encryption_version = encryption_version

    @property
    def content(self) -> List[Content]:
        return [c[0].name for c in self.__content.values()]

    # @property
    # def public_key(self):
    #     return self.__public_key

    # def get_private_key(self, user: UUID, private_key_user: str):
    #     key = self.get_key(user)
    #
    #     try:
    #         private_key = key.get_decryption_key()
    #     except ValueError:
    #         raise DomainError(
    #             "The key to access content of this folder is not working."
    #         )
    #
    #     return private_key

    # def get_key(self, user: Optional[UUID] = None) -> FolderKey:
    #     if user is not None:
    #         possible_keys = list(
    #             filter(
    #                 lambda k: k.user == user and not k.missing and k.correct,
    #                 self.__keys,
    #             )
    #         )
    #
    #         if len(possible_keys) > 1:
    #             raise DomainError("More than one possible key detected.")
    #
    #         if len(possible_keys) == 0:
    #             raise DomainError("No keys detected to access content in this folder.")
    #
    #         key = possible_keys
    #
    #         return key
    #
    #     else:
    #         return FolderKey(public_key=self.public_key)

    def get_asymmetric_encryption_class(
        self, direction: Literal["ENCRYPTION", "DECRYPTION"]
    ) -> Type[AsymmetricEncryption]:
        if direction == "DECRYPTION":
            return self.__encryption_hierarchy[self.__encryption_version]
        if direction == "ENCRYPTION":
            return self.__encryption_hierarchy[max(self.__encryption_hierarchy.keys())]

    def __reencrypt_all_keys(self, folder_key: FolderKey):
        encryption_class = self.get_asymmetric_encryption_class("ENCRYPTION")

        # get a new folder key
        private_key, public_key = encryption_class.generate_keys()
        new_folder_key = FolderKey(
            private_key=private_key,
            public_key=public_key,
            owner=folder_key.owner,
            folder_pk=self.__pk,
        )

        # decrypt content keys
        for content in self.__content.values():
            enc_content_key = content[1]
            content_key = enc_content_key.decrypt(folder_key)
            new_enc_content_key = content_key.encrypt(
                lock_key=new_folder_key, encryption_class=encryption_class
            )
            self.__content[content[0].name] = (content[0], new_enc_content_key)

        # reencrypt keys
        new_keys = []
        for key in self.__keys:
            new_key = FolderKey(
                owner=key.owner,
                folder_pk=self.__pk,
                private_key=new_folder_key.get_decryption_key(),
                public_key=new_folder_key.get_encryption_key(),
            )
            enc_new_key = new_key.encrypt()
            new_keys.append(enc_new_key)
        self.__keys = new_keys

        # update encryption version
        self.__encryption_version = max(self.__encryption_hierarchy.keys())

    def add_content(
        self, content: Content, content_key: ContentKey, folder_key: FolderKey
    ):
        encryption_class = self.get_asymmetric_encryption_class("ENCRYPTION")
        enc_content_key = content_key.encrypt(folder_key, encryption_class)
        if content.name in self.__content:
            raise DomainError(
                "This folder already contains an item with the same name."
            )
        self.__content[content.name] = (content, enc_content_key)
        self.__encryption_version = max(self.__encryption_hierarchy.keys())

    def update_content(
        self, content: Content, content_key: ContentKey, folder_key: FolderKey
    ):
        encryption_class = self.get_asymmetric_encryption_class("ENCRYPTION")
        enc_content_key = content_key.encrypt(folder_key, encryption_class)
        if content.name not in self.__content:
            raise DomainError("This folder does not contain an item with this name.")
        self.__content[content.name] = (content, enc_content_key)
        self.__encryption_version = max(self.__encryption_hierarchy.keys())

    def delete_content(self, content: Content):
        if content.name not in self.__content:
            raise DomainError("This folder does not contain an item with this name.")
        del self.__content[content.name]

    def get_content_key(self, content: Content, folder_key: FolderKey):
        if content.name not in self.__content:
            raise DomainError("This folder does not contain the specified item.")
        enc_content_key = self.__content[content.name][1]
        content_key = enc_content_key.decrypt(folder_key)
        return content_key

    def get_content_by_name(self, name: str) -> Content:
        if name not in self.__content:
            raise DomainError("This folder does not contain the specified item.")
        return self.__content[name][0]

    def move(self, target: "Folder"):
        # TODO
        pass

    # def grant_access(self, user: UUID, private_key_folder: Optional[str] = None):
    #
    #     if self.__public_key is None:
    #         private_key, public_key = self.__encryption_class.generate_keys()
    #         self.__public_key = public_key
    #         key = FolderKey(user, self, private_key, public_key)
    #
    #     else:
    #         assert private_key_folder is not None
    #         key = FolderKey(user, self, private_key_folder, self.__public_key)
    #
    #     self.__keys.append(key)
