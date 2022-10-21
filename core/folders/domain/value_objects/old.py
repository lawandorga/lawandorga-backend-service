# import abc
# from typing import Optional, Tuple
#
#
# class AsymmetricEncryption(abc.ABC):
#     def __init__(
#         self, enc_private_key: Optional[bytes] = None, public_key: Optional[str] = None
#     ):
#         if public_key is not None:
#             self.__public_key = public_key
#
#         if enc_private_key is not None:
#             self.__enc_private_key = enc_private_key
#
#         if public_key is None and enc_private_key is None:
#             private_key, public_key = self.__generate_key_pair()
#             self.__private_key = private_key
#             self.__public_key = public_key
#
#     @property
#     def public_key(self):
#         return self.__public_key
#
#     def encrypt(self, encryption: "AsymmetricEncryption"):
#         """Encrypts the own private_key with another encryption's encrypt_key method"""
#
#         self.__enc_private_key = encryption.encrypt_key(self.__private_key)
#
#     def decrypt(self, encryption: "AsymmetricEncryption"):
#         """Decrypts the own enc_private_key with another encryption's decrypt_key method"""
#
#         self.__private_key = encryption.decrypt_key(self.__enc_private_key)
#
#     def get_enc_private_key(self, encryption: "AsymmetricEncryption") -> bytes:
#         """Returns the encrypted private_key"""
#
#         if not hasattr(self, "__enc_private_key"):
#             self.encrypt(encryption)
#         return self.__enc_private_key
#
#     @abc.abstractmethod
#     def __generate_key_pair(self) -> Tuple[str, str]:
#         """Generates a private_key and public_key pair"""
#
#         pass
#
#     @abc.abstractmethod
#     def decrypt_key(self, key: bytes) -> str:
#         """Decrypts a key that was encrypted with the own public_key"""
#
#         pass
#
#     @abc.abstractmethod
#     def encrypt_key(self, key: str) -> bytes:
#         """Encrypts a key with the own public_key"""
#
#         pass
#
#
# ###########
#
# import abc
# from typing import Optional
#
# from apps.core.folders.domain.value_objects.asymmetric_encryption import (
#     AsymmetricEncryption,
# )
#
#
# class SymmetricEncryption(abc.ABC):
#     def __init__(self, enc_key: Optional[bytes] = None):
#         if enc_key is not None:
#             self.__enc_key = enc_key
#
#         else:
#             self.__key = self.__generate_key()
#
#     def encrypt(self, encryption: AsymmetricEncryption):
#         """Encrypts the own key with another encryption's encrypt_key method"""
#
#         self.__enc_key = encryption.encrypt_key(self.__key)
#
#     def decrypt(self, encryption: AsymmetricEncryption):
#         """Decrypts the own key with another encryption's decrypt_key method"""
#
#         self.__key = encryption.decrypt_key(self.__enc_key)
#
#     def get_enc_key(self, encryption: AsymmetricEncryption) -> bytes:
#         """Returns the encrypted key"""
#
#         if not hasattr(self, "__enc_key"):
#             self.encrypt(encryption)
#         return self.__enc_key
#
#     @abc.abstractmethod
#     def __generate_key(self) -> str:
#         """Generates a symmetric encryption key"""
#
#         pass
#
#     @abc.abstractmethod
#     def encrypt_data(self, data: str) -> bytes:
#         """Used to encrypt external stuff"""
#
#         pass
#
#     @abc.abstractmethod
#     def decrypt_data(self, data: bytes) -> str:
#         """Used to decrypt external stuff"""
#
#         pass
