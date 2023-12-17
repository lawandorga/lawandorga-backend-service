import abc
from typing import Literal, Type


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


class EncryptionWarehouse:
    __ASYMMETRIC_ENCRYPTION_HIERARCHY: dict[str, Type[AsymmetricEncryption]] = {}
    __SYMMETRIC_ENCRYPTION_HIERARCHY: dict[str, Type[SymmetricEncryption]] = {}
    __HIGHEST_ASYMMETRIC_ENCRYPTION: Type[AsymmetricEncryption]
    __HIGHEST_SYMMETRIC_ENCRYPTION: Type[SymmetricEncryption]

    @classmethod
    def reset_encryption_hierarchies(cls):
        cls.__ASYMMETRIC_ENCRYPTION_HIERARCHY = {}
        cls.__SYMMETRIC_ENCRYPTION_HIERARCHY = {}

    @classmethod
    def add_asymmetric_encryption(cls, encryption: Type[AsymmetricEncryption]):
        assert encryption.VERSION

        if not encryption.VERSION.startswith("A"):
            raise ValueError("The version needs to start with 'A'.")

        if (
            encryption.VERSION in cls.__ASYMMETRIC_ENCRYPTION_HIERARCHY
            and encryption != cls.__ASYMMETRIC_ENCRYPTION_HIERARCHY[encryption.VERSION]
        ):
            raise ValueError("This encryption level is already occupied.")

        cls.__ASYMMETRIC_ENCRYPTION_HIERARCHY[encryption.VERSION] = encryption
        cls.__HIGHEST_ASYMMETRIC_ENCRYPTION = encryption

    @classmethod
    def add_symmetric_encryption(cls, encryption: Type[SymmetricEncryption]):
        assert encryption.VERSION

        if not encryption.VERSION.startswith("S"):
            raise ValueError("The version needs to start with 'S'.")

        if (
            encryption.VERSION in cls.__SYMMETRIC_ENCRYPTION_HIERARCHY
            and encryption != cls.__SYMMETRIC_ENCRYPTION_HIERARCHY[encryption.VERSION]
        ):
            raise ValueError("This encryption level is already occupied.")

        cls.__SYMMETRIC_ENCRYPTION_HIERARCHY[encryption.VERSION] = encryption
        cls.__HIGHEST_SYMMETRIC_ENCRYPTION = encryption

    @classmethod
    def get_highest_asymmetric_encryption(cls):
        return cls.__HIGHEST_ASYMMETRIC_ENCRYPTION

    @classmethod
    def get_highest_symmetric_encryption(cls):
        return cls.__HIGHEST_SYMMETRIC_ENCRYPTION

    @classmethod
    def get_highest_versions(cls):
        return [
            cls.get_highest_symmetric_encryption().VERSION,
            cls.get_highest_asymmetric_encryption().VERSION,
        ]

    @classmethod
    def get_encryption_class(cls, version: str):
        if version.startswith("A") and version in cls.__ASYMMETRIC_ENCRYPTION_HIERARCHY:
            return cls.__ASYMMETRIC_ENCRYPTION_HIERARCHY[version]

        elif (
            version.startswith("S") and version in cls.__SYMMETRIC_ENCRYPTION_HIERARCHY
        ):
            return cls.__SYMMETRIC_ENCRYPTION_HIERARCHY[version]

        else:
            raise ValueError(
                "The encryption version '{}' could not be found within the hierarchy.".format(
                    version
                )
            )
