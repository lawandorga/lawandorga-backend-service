import time
from typing import Optional, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from core.folders.domain.value_objects.encryption import AsymmetricEncryption


class AsymmetricEncryptionV1(AsymmetricEncryption):
    VERSION = "A1"

    def __init__(
        self, private_key: Optional[str] = None, public_key: Optional[str] = None
    ):
        self.__private_key = private_key
        self.__public_key = public_key
        super().__init__()

    @classmethod
    def generate_keys(cls) -> Tuple[str, str, str]:
        t1 = time.time()
        generated_private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        bytes_private_key = generated_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )

        generated_public_key = generated_private_key.public_key()
        bytes_public_key = generated_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        private_key = bytes_private_key.decode("utf-8")
        public_key = bytes_public_key.decode("utf-8")
        print("KEY-GEN in {}s".format(time.time() - t1))

        return private_key, public_key, cls.VERSION

    def encrypt(self, data: bytes) -> bytes:
        assert self.__public_key is not None

        t1 = time.time()
        bytes_public_key = self.__public_key.encode("utf-8")
        object_public_key: rsa.RSAPublicKey = serialization.load_pem_public_key(  # type: ignore
            bytes_public_key, backend=default_backend()
        )

        enc_key = object_public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        print("EN-CRYPTED {} in {}s".format(data.decode("utf-8"), time.time() - t1))

        return enc_key

    def decrypt(self, enc_data: bytes) -> bytes:
        assert self.__private_key is not None

        t1 = time.time()
        bytes_private_key = self.__private_key.encode("utf-8")
        object_private_key: rsa.RSAPrivateKey = serialization.load_pem_private_key(  # type: ignore
            bytes_private_key, None, backend=default_backend()
        )

        data = object_private_key.decrypt(
            enc_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        print("DE-CRYPTED {} in {}s".format(data.decode("utf-8"), time.time() - t1))

        return data
