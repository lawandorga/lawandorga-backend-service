import abc
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from core.folders.domain.value_objects.keys import (
        AsymmetricKey,
        EncryptedAsymmetricKey,
        SymmetricKey,
    )


class IOwner:
    slug: Any

    @abc.abstractmethod
    def get_encryption_key(
        self, *args, **kwargs
    ) -> Union["AsymmetricKey", "SymmetricKey", "EncryptedAsymmetricKey"]:
        pass

    @abc.abstractmethod
    def get_decryption_key(
        self, *args, **kwargs
    ) -> Union["AsymmetricKey", "SymmetricKey"]:
        pass
