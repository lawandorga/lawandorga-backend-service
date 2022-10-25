from .base import AsymmetricKey, SymmetricKey
from .content_key import ContentKey
from .folder_key import FolderKey
from .user_key import UserKey


# refactor later into value objects files
class PasswordKey(SymmetricKey):
    def __init__(self, password: str):
        self.__key = password

    def get_key(self):
        return self.__key
