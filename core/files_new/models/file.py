import re
import unicodedata
from typing import Optional, cast
from uuid import UUID, uuid4

from django.core.files.storage import default_storage
from django.db import models

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.domain.repositiories.item import ItemRepository
from core.folders.infrastructure.django_item import DjangoItem
from core.records.models.record import Record
from core.rlc.models import Org
from core.seedwork.repository import RepositoryWarehouse
from core.seedwork.storage import download_and_decrypt_file, encrypt_and_upload_file
from core.seedwork.storage_folders import get_storage_folder_encrypted_record_document


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
    key = models.SlugField(allow_unicode=True, max_length=1000, unique=True)
    exists = models.BooleanField(default=True)

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

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.key = self.slugify()
        super().save(*args, **kwargs)

    def slugify(self, unique=""):
        key = "core/files_new/{}/{}".format(unique, self.name)
        special_char_map = {
            ord("ä"): "ae",
            ord("ü"): "ue",
            ord("ö"): "oe",
            ord("ß"): "ss",
            ord("Ä"): "AE",
            ord("Ö"): "OE",
            ord("Ü"): "UE",
        }
        key = key.translate(special_char_map)
        key = (
            unicodedata.normalize("NFKC", key).encode("ascii", "ignore").decode("ascii")
        )
        key = re.sub(r"[^/.\w\s-]", "", key.lower()).strip()
        key = re.sub(r"[-\s]+", "-", key)
        if not EncryptedRecordDocument.objects.filter(key=key).exists():
            return key
        else:
            unique = 1 if unique == "" else int(unique) + 1
            return self.slugify(unique=unique)

    def get_key(self):
        if not self.key:
            self.key = "{}{}".format(
                get_storage_folder_encrypted_record_document(
                    self.record.template.rlc.pk, self.record.id
                ),
                self.name,
            )
            self.save()
        return self.key

    def get_file_key(self):
        return "{}.enc".format(self.get_key())

    def upload(self, file, record_key):
        key = self.get_file_key()
        encrypt_and_upload_file(file, key, record_key)

    def download(self, record_key):
        key = self.get_file_key()
        return download_and_decrypt_file(key, record_key)

    def delete_on_cloud(self):
        key = self.get_file_key()
        default_storage.delete(key)

    def exists_on_s3(self):
        key = self.get_file_key()
        return default_storage.exists(key)
