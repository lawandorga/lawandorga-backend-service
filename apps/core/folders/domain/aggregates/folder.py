from typing import List, Literal, Optional, Tuple, Type

from apps.core.folders.domain.aggregates.content import Content
from apps.core.folders.domain.value_objects.encryption import AsymmetricEncryption
from apps.core.folders.domain.value_objects.key import ContentKey, FolderKey

# from uuid import UUID


# from apps.static.domain_layer import DomainError


class Folder:
    def __init__(
        self,
        # pk: UUID,
        name: str,
        # parent: Optional["Folder"],
        encryption_class: AsymmetricEncryption,
        asymmetric_encryption_hierarchy: dict[int, Type[AsymmetricEncryption]],
        encryption_version=0,
        keys: List[FolderKey] = None,
        public_key: Optional[str] = None,
        children: List[Tuple[Content, ContentKey]] = None,
    ):
        # self.__pk = pk
        self.__name = name
        # self.__parent = parent
        self.__public_key = public_key
        self.__children = children if children is not None else []
        self.__keys = keys if keys is not None else []
        self.__encryption_class = encryption_class
        self.__encryption_hierarchy = asymmetric_encryption_hierarchy
        self.__encryption_version = encryption_version

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

    def add_content(
        self, content: Content, content_key: ContentKey, folder_key: FolderKey
    ):
        encryption_class = self.get_asymmetric_encryption_class("ENCRYPTION")
        enc_content_key = content_key.encrypt(folder_key, encryption_class)
        self.__children.append((content, enc_content_key))

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
