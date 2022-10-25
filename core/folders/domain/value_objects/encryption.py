import abc
from typing import Literal, Type, Union


class Encryption(abc.ABC):
    ENCRYPTION_TYPE: Literal["ASYMMETRIC", "SYMMETRIC", None] = None
    VERSION: Union[str, None] = None

    def __init__(self, *args, **kwargs):
        assert self.VERSION is not None

    @abc.abstractmethod
    def encrypt(self, data: bytes) -> bytes:
        pass

    @abc.abstractmethod
    def decrypt(self, enc_data: bytes) -> bytes:
        pass


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


class EncryptionPyramid:
    ASYMMETRIC_ENCRYPTION_HIERARCHY: dict[str, Type[AsymmetricEncryption]] = {}
    SYMMETRIC_ENCRYPTION_HIERARCHY: dict[str, Type[SymmetricEncryption]] = {}

    @classmethod
    def reset_encryption_hierarchies(cls):
        cls.ASYMMETRIC_ENCRYPTION_HIERARCHY = {}
        cls.SYMMETRIC_ENCRYPTION_HIERARCHY = {}

    @classmethod
    def add_asymmetric_encryption(cls, encryption: Type[AsymmetricEncryption]):
        assert encryption.VERSION

        if not encryption.VERSION.startswith("A"):
            raise ValueError("The version needs to start with 'A'.")

        if encryption.VERSION in cls.ASYMMETRIC_ENCRYPTION_HIERARCHY:
            raise ValueError("This encryption level is already occupied.")

        cls.ASYMMETRIC_ENCRYPTION_HIERARCHY[encryption.VERSION] = encryption

    @classmethod
    def add_symmetric_encryption(cls, encryption: Type[SymmetricEncryption]):
        assert encryption.VERSION

        if not encryption.VERSION.startswith("S"):
            raise ValueError("The version needs to start with 'S'.")

        if encryption.VERSION in cls.SYMMETRIC_ENCRYPTION_HIERARCHY:
            raise ValueError("This encryption level is already occupied.")

        cls.SYMMETRIC_ENCRYPTION_HIERARCHY[encryption.VERSION] = encryption

    @classmethod
    def get_asymmetric_encryption_hierarchy(cls):
        return cls.ASYMMETRIC_ENCRYPTION_HIERARCHY

    @classmethod
    def get_symmetric_encryption_hierarchy(cls):
        return cls.SYMMETRIC_ENCRYPTION_HIERARCHY

    @classmethod
    def get_encryption_class(cls, version: str):
        if version.startswith("A") and version in cls.ASYMMETRIC_ENCRYPTION_HIERARCHY:
            return cls.ASYMMETRIC_ENCRYPTION_HIERARCHY[version]

        elif version.startswith("S") and version in cls.SYMMETRIC_ENCRYPTION_HIERARCHY:
            return cls.SYMMETRIC_ENCRYPTION_HIERARCHY[version]

        else:
            raise ValueError(
                "The encryption version '{}' could not be found within the hierarchy.".format(
                    version
                )
            )
