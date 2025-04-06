from typing import TYPE_CHECKING
from uuid import UUID

from django.db import models

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.aggregates.item import FolderItem
from core.folders.domain.value_objects.encryption import EncryptionDecryptionError
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from messagebus.domain.collector import EventCollector

if TYPE_CHECKING:
    from core.auth.models.org_user import OrgUser

    _Base = models.Model
else:
    _Base = object


class DeleteFolderItemMixin(_Base):
    REPOSITORY: str
    org_id: int
    uuid: UUID | models.UUIDField
    name: str | models.CharField
    folder_uuid: UUID | models.UUIDField

    def delete(self, collector: EventCollector, *args, **kwargs) -> None:  # type: ignore
        collector.collect(
            FolderItem.ItemDeleted(
                org_pk=self.org_id,
                uuid=self.uuid,
                repository=self.REPOSITORY,
                name=self.name,
                folder_uuid=self.folder_uuid,
            )
        )
        super().delete(*args, **kwargs)


class PutFolderItemIntoFolderMixin(_Base):
    REPOSITORY: str
    org_id: int
    uuid: UUID | models.UUIDField
    name: str | models.CharField
    folder_uuid: UUID | models.UUIDField

    def put_into_folder(self, folder: Folder, collector: EventCollector) -> None:
        assert self.folder_uuid is None
        self.folder_uuid = folder.uuid
        self._folder = folder
        collector.collect(
            FolderItem.ItemAddedToFolder(
                org_pk=self.org_id,
                uuid=self.uuid,
                repository=self.REPOSITORY,
                name=self.name,
                folder_uuid=self.folder_uuid,  # type: ignore
            )
        )


class RenameFolderItemMixin(_Base):
    REPOSITORY: str
    org_id: int
    uuid: UUID | models.UUIDField
    name: str | models.CharField
    folder_uuid: UUID | models.UUIDField

    def renamed(self, collector: EventCollector) -> None:
        collector.collect(
            FolderItem.ItemRenamed(
                org_pk=self.org_id,
                uuid=self.uuid,
                repository=self.REPOSITORY,
                name=self.name,
                folder_uuid=self.folder_uuid,
            )
        )


class FolderItemMixin(
    PutFolderItemIntoFolderMixin, RenameFolderItemMixin, DeleteFolderItemMixin
):
    @property
    def folder(self) -> Folder:
        assert self.folder_uuid is not None
        if not hasattr(self, "_folder") or getattr(self, "_folder", None) is None:
            r = DjangoFolderRepository()
            self._folder = r.retrieve(self.org_id, self.folder_uuid)
        assert self._folder is not None
        return self._folder

    def get_decryption_key(self, requestor: "OrgUser"):
        try:
            return self.folder.get_decryption_key(requestor=requestor)
        except EncryptionDecryptionError as e:
            folder = self.folder.get_folder_of_access(requestor)
            if folder is not None:
                folder.invalidate_keys_of(requestor)
                r = DjangoFolderRepository()
                r.save(folder)
            raise e

    def get_encryption_key(self, requestor: "OrgUser"):
        return self.folder.get_encryption_key(requestor=requestor)

    def has_access(self, user: "OrgUser"):
        return self.folder.has_access(user)
