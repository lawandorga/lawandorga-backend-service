import abc
from typing import Literal


class EncryptionDecryptionError(Exception):
    def __init__(self, exc: Exception) -> None:
        super().__init__()
        self.exc = exc

    def __str__(self) -> str:
        return f"Encryption/Decryption error: {self.exc}"


class Encryption:
    ENCRYPTION_TYPE: Literal["ASYMMETRIC", "SYMMETRIC"]
    VERSION: str

    def __init__(self, *args, **kwargs):
        assert self.VERSION is not None

    def encrypt(self, data: bytes) -> bytes:
        raise NotImplementedError()

    def decrypt(self, enc_data: bytes) -> bytes:
        raise NotImplementedError()


class AsymmetricEncryption(Encryption):
    ENCRYPTION_TYPE: Literal["ASYMMETRIC"] = "ASYMMETRIC"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.VERSION.startswith("A")

    @staticmethod
    @abc.abstractmethod
    def generate_keys() -> tuple[str, str, str]:
        pass


class SymmetricEncryption(Encryption):
    ENCRYPTION_TYPE: Literal["SYMMETRIC"] = "SYMMETRIC"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.VERSION.startswith("S")

    @staticmethod
    @abc.abstractmethod
    def generate_key() -> tuple[str, str]:
        pass
