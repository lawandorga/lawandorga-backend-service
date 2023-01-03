from typing import Optional, cast
from uuid import UUID, uuid4

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.db import models

from core.auth.models import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.domain.repositiories.item import ItemRepository
from core.folders.domain.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)
from core.folders.infrastructure.django_item import DjangoItem
from core.records.models.record import Record
from core.rlc.models import Org
from core.seedwork.repository import RepositoryWarehouse
from core.seedwork.storage import download_and_decrypt_file, encrypt_and_upload_file


class DjangoFileRepository(ItemRepository):
    IDENTIFIER = "FILE"

    @classmethod
    def retrieve(
        cls, uuid: UUID, org_pk: Optional[int] = None
    ) -> "EncryptedRecordDocument":
        assert isinstance(uuid, UUID)
        return EncryptedRecordDocument.objects.get(uuid=uuid)


class EncryptedRecordDocument(DjangoItem, models.Model):
    REPOSITORY = "FILE"

    name = models.CharField(max_length=200)
    record = models.ForeignKey(
        Record, related_name="documents", on_delete=models.CASCADE, null=True
    )
    org = models.ForeignKey(Org, related_name="files", on_delete=models.CASCADE)
    uuid = models.UUIDField(db_index=True, unique=True, default=uuid4)
    folder_uuid = models.UUIDField(db_index=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    file_size = models.BigIntegerField(null=True)
    location = models.SlugField(allow_unicode=True, max_length=1000, unique=True)
    exists = models.BooleanField(default=True)
    key = models.JSONField(null=True)

    class Meta:
        verbose_name = "RecordDocument"
        verbose_name_plural = "RecordDocuments"

    def __str__(self):
        return "recordDocument: {}; name: {}; record: {};".format(
            self.pk, self.name, self.record.id
        )

    @property
    def org_pk(self) -> int:
        assert self.org_id is not None
        return self.org_id

    @property
    def folder(self) -> Optional[Folder]:
        assert self.org_id is not None
        if self.folder_uuid is None:
            return None
        if not hasattr(self, "_folder"):
            r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
            self._folder = r.retrieve(self.org_id, self.folder_uuid)
        return self._folder

    @property
    def actions(self):
        return {}

    def set_name(self, name: str):
        assert self.org_id is not None
        super().set_name(name)
        self.name = name

    def generate_key(self, user: RlcUser):
        assert self.folder is not None and self.key is None
        key = SymmetricKey.generate()
        lock_key = self.folder.get_encryption_key(requestor=user)
        enc_key = EncryptedSymmetricKey.create(key, lock_key)
        self.key = enc_key.as_dict()

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.set_location()
        super().save(*args, **kwargs)

    def set_location(self):
        assert self.location is None or self.location == ""
        self.location = "core/files_new/{}/{}".format(self.folder.uuid, uuid4())

    def __get_file_key(self):
        return "{}.enc".format(self.location)

    def __get_key(self, user: RlcUser):
        assert self.folder is not None

        decryption_key = self.folder.get_decryption_key(requestor=user)
        enc_key = EncryptedSymmetricKey.create_from_dict(self.key)
        key = enc_key.decrypt(decryption_key)

        return key.get_key()

    def upload(self, file: UploadedFile, by: RlcUser):
        key = self.__get_key(by)
        location = self.__get_file_key()
        encrypt_and_upload_file(file, location, key)

    def download(self, by: RlcUser):
        key = self.__get_key(by)
        location = self.__get_file_key()
        return download_and_decrypt_file(location, key)

    def delete_on_cloud(self):
        key = self.__get_file_key()
        default_storage.delete(key)

    def exists_on_s3(self):
        key = self.__get_file_key()
        return default_storage.exists(key)
