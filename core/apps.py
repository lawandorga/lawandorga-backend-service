from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"

    def ready(self) -> None:
        from core.folders.domain.value_objects.encryption import EncryptionWarehouse
        from core.folders.infrastructure.asymmetric_encryptions import (
            AsymmetricEncryptionV1,
        )
        from core.folders.infrastructure.folder_repository import DjangoFolderRepository
        from core.folders.infrastructure.symmetric_encryptions import (
            SymmetricEncryptionV1,
        )
        from core.records.models.record import DjangoRecordRepository
        from core.seedwork.repository import RepositoryWarehouse

        EncryptionWarehouse.add_asymmetric_encryption(AsymmetricEncryptionV1)
        EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionV1)
        RepositoryWarehouse.add_repository(DjangoFolderRepository)
        RepositoryWarehouse.add_repository(DjangoRecordRepository)

        # call the sub ready methods
        from core.folders.ready import ready

        ready()
