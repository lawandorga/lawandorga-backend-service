from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding, rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from hashlib import sha3_256
from enum import Enum
import tempfile
import secrets
import string
import struct
import os


class OutputType(Enum):
    STRING = 1
    BYTES = 2


def get_bytes_from_string_or_return_bytes(key):
    if isinstance(key, str):
        return bytes(key, "utf-8")
    return key


def get_string_from_bytes_or_return_string(pot_bytes):
    if isinstance(pot_bytes, bytes):
        return pot_bytes.decode("utf-8")
    return pot_bytes


class AESEncryption:
    @staticmethod
    def generate_iv() -> bytes:
        return os.urandom(16)

    @staticmethod
    def generate_secure_key() -> str:
        password_characters = string.ascii_letters + string.digits + string.punctuation
        return "".join(secrets.choice(password_characters) for i in range(64))

    @staticmethod
    def encrypt_with_iv(msg: str, key: str, iv: bytes):
        msg = get_bytes_from_string_or_return_bytes(msg)
        key = get_bytes_from_string_or_return_bytes(key)
        hashed_key_bytes = sha3_256(key).digest()
        cipher = AES.new(hashed_key_bytes, AES.MODE_CBC, iv)
        if isinstance(msg, memoryview):
            msg = bytes(msg)
        cipher_bytes = cipher.encrypt(pad(msg, AES.block_size))
        return cipher_bytes

    @staticmethod
    def decrypt_with_iv(encrypted, key, iv, output_type=OutputType.STRING):
        if encrypted.__len__() == 0:
            if output_type == OutputType.STRING:
                return ""
            return encrypted
        key = get_bytes_from_string_or_return_bytes(key)
        hashed_key_bytes = sha3_256(key).digest()
        cipher = AES.new(hashed_key_bytes, AES.MODE_CBC, iv)
        if isinstance(encrypted, memoryview):
            encrypted = bytes(encrypted)
        plaintext_bytes = unpad(cipher.decrypt(encrypted), AES.block_size)
        if output_type == OutputType.STRING:
            return get_string_from_bytes_or_return_string(plaintext_bytes)
        return plaintext_bytes

    @staticmethod
    def encrypt(msg: str, key: str) -> bytes:
        """
        :param msg: bytes/string, message which shall be encrypted
        :param key: bytes/string, key with which to encrypt
        :return: bytes, encrypted message (with iv at the beginning
        """
        if msg is None or msg.__len__() == 0:
            return bytearray()
        iv: bytes = AESEncryption.generate_iv()
        cipher_bytes = AESEncryption.encrypt_with_iv(msg, key, iv)
        cipher_bytes = iv + cipher_bytes
        return cipher_bytes

    @staticmethod
    def decrypt(encrypted, key, output_type=OutputType.STRING):
        iv = encrypted[:16]
        real_encrypted = encrypted[16:]
        plain = AESEncryption.decrypt_with_iv(real_encrypted, key, iv, output_type)
        return plain

    @staticmethod
    def encrypt_file(file, key):
        chunk_size = 64 * 1024
        key = get_bytes_from_string_or_return_bytes(key)
        hashed_key_bytes = sha3_256(key).digest()
        encrypted_file = '{}.enc'.format(file)
        file_size = os.path.getsize(file)
        iv = AESEncryption.generate_iv()
        encryptor = AES.new(hashed_key_bytes, AES.MODE_CBC, iv)

        with open(file, "rb") as infile:
            with open(encrypted_file, "wb") as outfile:
                outfile.write(struct.pack("<Q", file_size))
                outfile.write(iv)

                while True:
                    chunk = infile.read(chunk_size)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += b" " * (16 - len(chunk) % 16)
                    outfile.write(encryptor.encrypt(chunk))

        return encrypted_file

    @staticmethod
    def decrypt_file(file, key, output_file_name=None):
        chunk_size = 64 * 1024
        key = get_bytes_from_string_or_return_bytes(key)
        hashed_key_bytes = sha3_256(key).digest()

        if not output_file_name:
            output_file_name = os.path.splitext(file)[0]  # removes .enc extension

        with open(file, "rb") as infile:
            org_size = struct.unpack("<Q", infile.read(struct.calcsize("Q")))[0]
            iv = infile.read(16)
            decryptor = AES.new(hashed_key_bytes, AES.MODE_CBC, iv)

            with open(output_file_name, "wb") as outfile:
                while True:
                    chunk = infile.read(chunk_size)
                    if len(chunk) == 0:
                        break
                    outfile.write(decryptor.decrypt(chunk))

                outfile.truncate(org_size)

    @staticmethod
    def encrypt_in_memory_file(file, aes_key):
        # fix the aes key
        aes_key = get_bytes_from_string_or_return_bytes(aes_key)
        # stuff needed
        chunk_size = 64 * 1024
        hashed_key_bytes = sha3_256(aes_key).digest()
        iv = AESEncryption.generate_iv()
        encryptor = AES.new(hashed_key_bytes, AES.MODE_CBC, iv)
        # encrypt the file
        encrypted_file = tempfile.TemporaryFile('wb+')
        encrypted_file.write(struct.pack("<Q", file.size))
        encrypted_file.write(iv)
        while True:
            chunk = file.read(chunk_size)
            if len(chunk) == 0:
                break
            elif len(chunk) % 16 != 0:
                chunk += b" " * (16 - len(chunk) % 16)
            encrypted_file.write(encryptor.encrypt(chunk))
        # fix the file
        encrypted_file.seek(0)
        # return
        return encrypted_file

    @staticmethod
    def decrypt_bytes_file(file, aes_key):
        # fix the aes key
        aes_key = get_bytes_from_string_or_return_bytes(aes_key)
        # stuff needed
        chunk_size = 64 * 1024
        hashed_key_bytes = sha3_256(aes_key).digest()
        org_size = struct.unpack("<Q", file.read(struct.calcsize("Q")))[0]
        iv = file.read(16)
        decryptor = AES.new(hashed_key_bytes, AES.MODE_CBC, iv)
        # decrypt
        outfile = tempfile.TemporaryFile('wb+')
        while True:
            chunk = file.read(chunk_size)
            if len(chunk) == 0:
                break
            outfile.write(decryptor.decrypt(chunk))
        # improve the file
        outfile.truncate(org_size)
        outfile.seek(0)
        # return
        return outfile


class RSAEncryption:
    @staticmethod
    def generate_keys() -> (bytes, bytes):
        """
        generates private and public RSA key pair

        :return: private bytes and public bytes
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_key = private_key.public_key()
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return pem_private, pem_public

    @staticmethod
    def encrypt(msg, pem_public_key):
        msg = get_bytes_from_string_or_return_bytes(msg)

        public_key = serialization.load_pem_public_key(
            pem_public_key, backend=default_backend()
        )
        ciphertext = public_key.encrypt(
            msg,
            asymmetric_padding.OAEP(
                mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return ciphertext

    @staticmethod
    def decrypt(ciphertext, pem_private_key, output_type=OutputType.STRING):
        pem_private_key = get_bytes_from_string_or_return_bytes(pem_private_key)
        private_key = serialization.load_pem_private_key(
            pem_private_key, None, backend=default_backend()
        )

        if not isinstance(ciphertext, bytes):
            try:
                ciphertext = ciphertext.tobytes()
            except Exception as e:
                raise Exception("error at decrypting, wrong type: ", e)

        plaintext = private_key.decrypt(
            ciphertext,
            asymmetric_padding.OAEP(
                mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        if output_type == OutputType.STRING:
            return get_string_from_bytes_or_return_string(plaintext)
        return plaintext


class EncryptedModelMixin(object):
    encrypted_fields = []
    encryption_class = RSAEncryption

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ) -> None:
        for field in self.encrypted_fields:
            data_in_field = getattr(self, field)
            if data_in_field and not (isinstance(data_in_field, bytes) or isinstance(data_in_field, memoryview)):
                raise ValueError(
                    "The field {} of object {} is not encrypted. "
                    "Do not save unencrypted data. "
                    "Value of the field: {}.".format(field, self, data_in_field)
                )
        super().save(force_insert, force_update, using, update_fields)

    def decrypt(self, key: str or bytes) -> None:
        if getattr(self, 'encryption_status', '') != 'DECRYPTED':
            for field in self.encrypted_fields:
                decrypted_field = self.encryption_class.decrypt(getattr(self, field), key)
                setattr(self, field, decrypted_field)
        setattr(self, 'encryption_status', 'DECRYPTED')

    def encrypt(self, key: str or bytes) -> None:
        if getattr(self, 'encryption_status', '') != 'ENCRYPTED':
            for field in self.encrypted_fields:
                encrypted_field = self.encryption_class.encrypt(getattr(self, field), key)
                setattr(self, field, encrypted_field)
        setattr(self, 'encryption_status', 'ENCRYPTED')

    def reset_encrypted_fields(self):
        for field in self.encrypted_fields:
            setattr(self, field, None)
