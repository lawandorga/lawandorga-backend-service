from core.folders.domain.value_objects.keys.base import AsymmetricKey


class UserKey(AsymmetricKey):
    def __init__(self, private_key: str, public_key: str, origin: str):
        self.__private_key = private_key
        self.__public_key = public_key
        self._origin = origin

        super().__init__()

    def get_decryption_key(self) -> str:
        return self.__private_key

    def get_encryption_key(self) -> str:
        return self.__public_key
