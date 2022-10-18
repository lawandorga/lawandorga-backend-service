import abc
from typing import Literal, Tuple


class Encryption(abc.ABC):
    ENCRYPTION_TYPE: Literal["ASYMMETRIC", "SYMMETRIC", None] = None

    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def encrypt(self, data: bytes) -> bytes:
        pass

    @abc.abstractmethod
    def decrypt(self, enc_data: bytes) -> bytes:
        pass


class AsymmetricEncryption(Encryption):
    ENCRYPTION_TYPE: Literal["ASYMMETRIC"] = "ASYMMETRIC"

    @staticmethod
    @abc.abstractmethod
    def generate_keys() -> Tuple[str, str]:
        pass


class SymmetricEncryption(Encryption):
    ENCRYPTION_TYPE: Literal["SYMMETRIC"] = "SYMMETRIC"

    @staticmethod
    @abc.abstractmethod
    def generate_key() -> str:
        pass
