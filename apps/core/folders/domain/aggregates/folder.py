from typing import List, Optional
from uuid import UUID

from apps.core.folders.domain.value_objects.encryption import AsymmetricEncryption
from apps.core.folders.domain.value_objects.key import FolderKey
from apps.static.domain_layer import DomainError


class Folder:
    def __init__(
        self,
        # pk: UUID,
        name: str,
        # parent: Optional["Folder"],
        encryption_class: AsymmetricEncryption,
        keys: List[FolderKey] = None,
        public_key: Optional[str] = None,
        # children: List[Content],
    ):
        # self.__pk = pk
        self.__name = name
        # self.__parent = parent
        self.__public_key = public_key
        # self.__children = children
        self.__keys = keys if keys is not None else []
        self.__encryption_class = encryption_class

    @property
    def public_key(self):
        return self.__public_key

    def get_private_key(self, user: UUID, private_key_user: str):
        key = self.get_key(user)

        try:
            private_key = key.get_decryption_key()
        except ValueError:
            raise DomainError(
                "The key to access content of this folder is not working."
            )

        return private_key

    def get_key(self, user: Optional[UUID] = None) -> FolderKey:
        if user is not None:
            possible_keys = list(
                filter(
                    lambda k: k.user == user and not k.missing and k.correct,
                    self.__keys,
                )
            )

            if len(possible_keys) > 1:
                raise DomainError("More than one possible key detected.")

            if len(possible_keys) == 0:
                raise DomainError("No keys detected to access content in this folder.")

            key = possible_keys

            return key

        else:
            return FolderKey(public_key=self.public_key)

    def move(self, target: "Folder"):
        # TODO
        pass

    def grant_access(self, user: UUID, private_key_folder: Optional[str] = None):

        if self.__public_key is None:
            private_key, public_key = self.__encryption_class.generate_keys()
            self.__public_key = public_key
            key = FolderKey(user, self, private_key, public_key)

        else:
            assert private_key_folder is not None
            key = FolderKey(user, self, private_key_folder, self.__public_key)

        self.__keys.append(key)
