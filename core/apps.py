from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"

    def ready(self) -> None:
        from core.collab.repositories.collab import CollabRepository
        from core.data_sheets.models.data_sheet import DjangoRecordRepository
        from core.files_new.models.file import DjangoFileRepository
        from core.folders.domain.value_objects.encryption import EncryptionWarehouse
        from core.folders.infrastructure.asymmetric_encryptions import (
            AsymmetricEncryptionV1,
        )
        from core.folders.infrastructure.folder_repository import DjangoFolderRepository
        from core.folders.infrastructure.symmetric_encryptions import (
            SymmetricEncryptionV1,
        )
        from core.questionnaires.models.questionnaire import (
            DjangoQuestionnaireRepository,
        )
        from core.records.models.record import DjangoRecordsRecordRepository
        from core.seedwork.repository import RepositoryWarehouse
        from core.upload.models.upload import DjangoUploadLinkRepository

        EncryptionWarehouse.add_asymmetric_encryption(AsymmetricEncryptionV1)
        EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionV1)
        RepositoryWarehouse.add_repository(DjangoFolderRepository)
        RepositoryWarehouse.add_repository(DjangoRecordRepository)
        RepositoryWarehouse.add_repository(DjangoFileRepository)
        RepositoryWarehouse.add_repository(DjangoQuestionnaireRepository)
        RepositoryWarehouse.add_repository(DjangoUploadLinkRepository)
        RepositoryWarehouse.add_repository(DjangoRecordsRecordRepository)
        RepositoryWarehouse.add_repository(CollabRepository())  # type: ignore

        # call the sub ready methods
        from core.folders.ready import ready

        ready()
