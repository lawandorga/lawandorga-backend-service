from typing import Optional

from core.folders.domain.aggregates.object import EncryptedObject


class CarWithSecretName(EncryptedObject):
    ENCRYPTED_FIELDS = ["name"]

    def __init__(self, enc_name: Optional[bytes] = None, name: Optional[str] = None):
        if isinstance(name, str):
            self.name = bytes(name, "utf-8")
        if isinstance(enc_name, bytes):
            self.name = enc_name
