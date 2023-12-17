from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"

    def ready(self) -> None:
        from core.folders.domain.value_objects.encryption import EncryptionWarehouse
        from core.folders.infrastructure.asymmetric_encryptions import (
            AsymmetricEncryptionV1,
        )
        from core.folders.infrastructure.symmetric_encryptions import (
            SymmetricEncryptionV1,
        )

        EncryptionWarehouse.add_asymmetric_encryption(AsymmetricEncryptionV1)
        EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionV1)

        # call the sub ready methods
        from core.folders.ready import ready

        ready()
