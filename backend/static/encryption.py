#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>
import secrets
import string

from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding, rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from backend.static.error_codes import ERROR__API__INVALID_PRIVATE_KEY
from Crypto.Util.Padding import pad, unpad
from backend.api.errors import CustomError
from Crypto.Cipher import AES
from hashlib import sha3_256
from enum import Enum
import struct
import os


class OutputType(Enum):
    STRING = 1
    BYTES = 2


def get_bytes_from_string_or_return_bytes(pot_string):
    if isinstance(pot_string, str):
        return bytes(pot_string, "utf-8")
    return pot_string


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
    def encrypt_field(source, destination, field_name, key):
        """
        reads field field_name from source, AES encrypts it with key and saves it with the same name to destination
        does nothing if field_name in source is none
        :param source:
        :param destination:
        :param field_name:
        :param key:
        :return:
        """
        if isinstance(source, dict):
            pass
        attr = getattr(source, field_name, None)
        if attr:
            setattr(destination, field_name, AESEncryption.encrypt(attr, key))

    @staticmethod
    def decrypt_field(source, destination, field_name, key):
        """
        reads field field_name from source, AES decrypts it with key and saves it with the same name to destination
        does nothing if field_name not in source
        :param source:
        :param destination:
        :param field_name:
        :param key:
        :return:
        """
        if isinstance(source, dict):
            if field_name in source:
                destination[field_name] = AESEncryption.decrypt(source[field_name], key)
        else:
            attr = getattr(source, field_name, None)
            if attr:
                # destination[field_name] = AESEncryption.decrypt(source[field_name], key)
                setattr(destination, field_name, AESEncryption.decrypt(attr, key))

    @staticmethod
    def encrypt_file(file, key):
        """

        :param file:
        :param key:
        :return: filepath to encrypted file AND filename of encrypted file
        """
        # TODO: refactor this, especiialy all those file_... vars
        chunk_size = 64 * 1024
        key = get_bytes_from_string_or_return_bytes(key)
        hashed_key_bytes = sha3_256(key).digest()
        file_index = file.rindex("/")
        file_path = file[:file_index]
        file_to_write = file[file_index + 1 :] + ".enc"
        file_size = os.path.getsize(file)
        iv = AESEncryption.generate_iv()
        encryptor = AES.new(hashed_key_bytes, AES.MODE_CBC, iv)

        with open(file, "rb") as infile:
            with open(os.path.join(file_path, file_to_write), "wb") as outfile:
                outfile.write(struct.pack("<Q", file_size))
                outfile.write(iv)

                while True:
                    chunk = infile.read(chunk_size)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += b" " * (16 - len(chunk) % 16)
                    outfile.write(encryptor.encrypt(chunk))
        return file + ".enc", file_to_write

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
            if data_in_field and not isinstance(data_in_field, bytes):
                raise ValueError(
                    "The field {} of object {} is not encrypted. Do not save unencrypted data.".format(
                        field, self
                    )
                )
        super().save(force_insert, force_update, using, update_fields)

    def decrypt(self, key: str or bytes) -> None:
        for field in self.encrypted_fields:
            decrypted_field = self.encryption_class.decrypt(getattr(self, field), key)
            setattr(self, field, decrypted_field)

    def encrypt(self, key: str or bytes) -> None:
        for field in self.encrypted_fields:
            encrypted_field = self.encryption_class.encrypt(getattr(self, field), key)
            setattr(self, field, encrypted_field)

    def reset_encrypted_fields(self):
        for field in self.encrypted_fields:
            setattr(self, field, None)
