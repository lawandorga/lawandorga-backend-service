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

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from enum import Enum


class OutputType(Enum):
    STRING = 1
    BYTES = 2


def get_bytes_from_string_or_return_bytes(pot_string):
    if isinstance(pot_string, str):
        return bytes(pot_string, 'utf-8')
    return pot_string


def get_string_from_bytes_or_return_string(pot_bytes):
    if isinstance(pot_bytes, bytes):
        return pot_bytes.decode('utf-8')
    return pot_bytes


class AESEncryption:
    @staticmethod
    def encrypt(msg, key, iv):
        msg = get_bytes_from_string_or_return_bytes(msg)
        backend = default_backend()

        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(msg) + padder.finalize()

        key = get_bytes_from_string_or_return_bytes(key)
        hasher = hashes.Hash(hashes.SHA3_256(), backend=backend)
        hasher.update(key)
        key_bytes = hasher.finalize()

        cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()

        return encryptor.update(padded_data) + encryptor.finalize()

    @staticmethod
    def decrypt(encrypted, key, iv, output_type=OutputType.STRING):
        backend = default_backend()

        key = get_bytes_from_string_or_return_bytes(key)
        hasher = hashes.Hash(hashes.SHA3_256(), backend=backend)
        hasher.update(key)
        key_bytes = hasher.finalize()

        cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        decrypted_bytes = decryptor.update(encrypted) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        unpadded_bytes = unpadder.update(decrypted_bytes) + unpadder.finalize()
        if output_type == OutputType.STRING:
            return get_string_from_bytes_or_return_string(unpadded_bytes)
        return unpadded_bytes


class RSAEncryption:
    @staticmethod
    def generate_keys():
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        pem_private = private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL,
                                        encryption_algorithm=serialization.NoEncryption())
        public_key = private_key.public_key()
        pem_public = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                             format=serialization.PublicFormat.SubjectPublicKeyInfo)
        return pem_private, pem_public

    @staticmethod
    def encrypt(msg, pem_public_key):
        msg = get_bytes_from_string_or_return_bytes(msg)

        public_key = serialization.load_pem_public_key(pem_public_key, backend=default_backend())
        ciphertext = public_key.encrypt(msg, asymmetric_padding.OAEP(
            mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(), label=None))
        return ciphertext

    @staticmethod
    def decrypt(ciphertext, pem_private_key, output_type=OutputType.STRING):
        private_key = serialization.load_pem_private_key(pem_private_key, None, backend=default_backend())
        plaintext = private_key.decrypt(ciphertext, asymmetric_padding.OAEP(
                                            mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
                                            algorithm=hashes.SHA256(), label=None))
        if output_type == OutputType.STRING:
            return get_string_from_bytes_or_return_string(plaintext)
        return plaintext
