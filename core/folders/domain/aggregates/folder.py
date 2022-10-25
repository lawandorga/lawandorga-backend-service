from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from core.folders.domain.aggregates.content import Content
from core.folders.domain.external import IUser
from core.folders.domain.value_objects.encryption import EncryptionPyramid
from core.folders.domain.value_objects.keys import ContentKey, FolderKey
from core.seedwork.domain_layer import DomainError


class Folder:
    @staticmethod
    def create(name: str = None):
        pk = uuid4()
        return Folder(name=name, pk=pk, keys=[], content={})

    def __init__(
        self,
        # parent: Optional["Folder"],
        name: str = None,
        pk: UUID = None,
        keys: List[FolderKey] = None,
        content: Dict[str, Tuple[Content, ContentKey]] = None,
    ):
        assert name is not None and pk is not None

        self.__pk = pk
        self.__name = name
        # self.__parent = parent
        self.__content = content if content is not None else {}
        self.__keys = (
            [k.encrypt() if k.is_encrypted else k for k in keys]
            if keys is not None
            else []
        )

    @property
    def content(self) -> List[Content]:
        return [c[0].name for c in self.__content.values()]

    @property
    def encryption_version(self) -> Optional[str]:
        if len(self.__keys) == 0:
            return None

        versions = []
        for key in self.__keys:
            versions.append(key.origin)

        if not all([v == versions[0] for v in versions]):
            raise Exception("Not all folder keys have the same encryption version.")

        return versions[0]

    def __reencrypt_all_keys(self, folder_key: FolderKey):
        encryption_class = EncryptionPyramid.get_highest_asymmetric_encryption()

        # get a new folder key
        private_key, public_key, version = encryption_class.generate_keys()
        new_folder_key = FolderKey.create(
            private_key=private_key,
            public_key=public_key,
            origin=version,
            owner=folder_key.owner,
        )

        # decrypt content keys
        new_content = {}
        for content in self.__content.values():
            enc_content_key = content[1]
            content_key = enc_content_key.decrypt(folder_key)
            new_enc_content_key = content_key.encrypt(new_folder_key)
            new_content[content[0].name] = (content[0], new_enc_content_key)

        # reencrypt keys
        new_keys = []
        for key in self.__keys:
            new_key = FolderKey.create(
                owner=key.owner,
                private_key=new_folder_key.get_decryption_key(),
                public_key=new_folder_key.get_encryption_key(),
                origin=new_folder_key.origin,
            )
            # enc_new_key = new_key.encrypt()
            new_keys.append(new_key)

        # set
        self.__content = new_content
        self.__keys = new_keys

    def __check_encryption_version(self, folder_key: FolderKey):
        encryption_class = EncryptionPyramid.get_highest_asymmetric_encryption()
        if self.encryption_version != encryption_class.VERSION:
            self.__reencrypt_all_keys(folder_key)

    def __find_folder_key(self, user: IUser) -> FolderKey:
        for key in self.__keys:
            if key.owner.slug == user.slug:
                return key
        raise DomainError("No folder key was found for this user.")

    def add_content(self, content: Content, content_key: ContentKey, user: IUser):
        if content.name in self.__content:
            raise DomainError(
                "This folder already contains an item with the same name."
            )
        folder_key = self.__find_folder_key(user)
        enc_content_key = content_key.encrypt(folder_key)
        self.__content[content.name] = (content, enc_content_key)
        # check
        self.__check_encryption_version(folder_key)

    def update_content(self, content: Content, content_key: ContentKey, user: IUser):
        if content.name not in self.__content:
            raise DomainError("This folder does not contain an item with this name.")
        folder_key = self.__find_folder_key(user)
        enc_content_key = content_key.encrypt(folder_key)
        self.__content[content.name] = (content, enc_content_key)
        # check
        self.__check_encryption_version(folder_key)

    def delete_content(self, content: Content):
        if content.name not in self.__content:
            raise DomainError("This folder does not contain an item with this name.")

        del self.__content[content.name]

    def get_content_key(self, content: Content, user: IUser):
        if content.name not in self.__content:
            raise DomainError("This folder does not contain the specified item.")

        folder_key = self.__find_folder_key(user)
        enc_content_key = self.__content[content.name][1]
        content_key = enc_content_key.decrypt(folder_key)
        return content_key

    def get_content_by_name(self, name: str) -> Content:
        if name not in self.__content:
            raise DomainError("This folder does not contain the specified item.")
        return self.__content[name][0]

    def move(self, target: "Folder"):
        pass

    def grant_access(self, to_user: IUser, by_user: Optional[IUser] = None):

        if len(self.__keys) == 0:
            encryption_class = EncryptionPyramid.get_highest_asymmetric_encryption()
            private_key, public_key, version = encryption_class.generate_keys()

        else:
            assert by_user is not None
            enc_folder_key = self.__find_folder_key(user=by_user)
            folder_key = enc_folder_key.decrypt()
            private_key = folder_key.get_decryption_key()
            public_key = folder_key.get_encryption_key()
            version = folder_key.origin

        key = FolderKey.create(owner=to_user, private_key=private_key, public_key=public_key, origin=version)
        enc_key = key.encrypt()
        self.__keys.append(enc_key)
