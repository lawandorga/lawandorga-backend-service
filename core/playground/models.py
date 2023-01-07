from typing import Any, Protocol, Union

from django.db import models

from core.folders.domain.external import IOwner
from core.folders.domain.value_objects.asymmetric_key import AsymmetricKey, EncryptedAsymmetricKey
from core.folders.domain.value_objects.symmetric_key import SymmetricKey


class Nameable(Protocol):
    uuid: Any

    def get_encryption_key(
        self, *args, **kwargs
    ) -> Union["AsymmetricKey", "SymmetricKey", "EncryptedAsymmetricKey"]:
        ...

    def get_decryption_key(
        self, *args, **kwargs
    ) -> Union["AsymmetricKey", "SymmetricKey"]:
        ...


class PlaygroundItem(models.Model):
    name = models.CharField(max_length=100)
    uuid = models.UUIDField()

    def get_encryption_key(
        self, *args, **kwargs
    ) -> Union["AsymmetricKey", "SymmetricKey", "EncryptedAsymmetricKey"]:
        return None

    def get_decryption_key(
        self, *args, **kwargs
    ) -> Union["AsymmetricKey", "SymmetricKey"]:
        return None


def print_my_uuid(item: Nameable):
    print(item.uuid)


print_my_uuid(PlaygroundItem(name='ABC'))
