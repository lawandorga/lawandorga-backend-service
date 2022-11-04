import abc
from typing import TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from core.folders.domain.value_objects.keys import (
        AsymmetricKey,
        EncryptedAsymmetricKey,
        EncryptedSymmetricKey,
        SymmetricKey,
    )


class IOwner(abc.ABC):
    slug: UUID

    @abc.abstractmethod
    def get_key(
        self,
    ) -> Union[
        "AsymmetricKey",
        "SymmetricKey",
        "EncryptedAsymmetricKey",
        "EncryptedSymmetricKey",
    ]:
        pass

    @abc.abstractmethod
    def get_encryption_key(self, *args, **kwargs) -> Union["AsymmetricKey", "SymmetricKey", "EncryptedAsymmetricKey"]:
        pass

    @abc.abstractmethod
    def get_decryption_key(self, *args, **kwargs) -> Union["AsymmetricKey", "SymmetricKey"]:
        pass
