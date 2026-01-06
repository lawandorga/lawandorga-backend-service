from typing import TYPE_CHECKING, Any, Protocol, Union

if TYPE_CHECKING:
    from core.encryption.value_objects.asymmetric_key import (
        AsymmetricKey,
        EncryptedAsymmetricKey,
    )
    from core.encryption.value_objects.symmetric_key import SymmetricKey


class IOwner(Protocol):
    uuid: Any

    def get_encryption_key(
        self, *args, **kwargs
    ) -> Union["AsymmetricKey", "SymmetricKey", "EncryptedAsymmetricKey"]: ...

    def get_decryption_key(
        self, *args, **kwargs
    ) -> Union["AsymmetricKey", "SymmetricKey"]: ...
