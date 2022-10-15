from typing import Optional

# from apps.core.folders.domain.value_objects.asymmetric_encryption import (
#     AsymmetricEncryption,
# )
from apps.core.folders.domain.value_objects.symmetric_encryption import (
    SymmetricEncryption,
)

# class PasswordInputEncryption(AsymmetricEncryption):
#     def __init__(self, password_user):
#         self.__password_user = password_user
#
#     def encrypt_key(self, key: str) -> bytes:
#         pass
#
#     def decrypt_key(self, key: bytes) -> str:
#         pass


class PasswordEncryption(SymmetricEncryption):
    def __init__(self, enc_private_key_user: Optional[bytes] = None):
        super().__init__(enc_private_key_user)

    def encrypt_data(self, data: str) -> bytes:
        """Used to encrypt external stuff"""

        pass

    def decrypt_data(self, data: bytes) -> str:
        """Used to decrypt external stuff"""

        pass
