from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.db import models

from core.auth.models import OrgUser
from core.encryption.infrastructure.symmetric_encryptions import SymmetricEncryptionV1
from core.encryption.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.item import ItemRepository
from core.folders.infrastructure.item_mixins import FolderItemMixin
from core.org.models import Org
from core.seedwork.storage import download_and_decrypt_file, encrypt_and_upload_file
from messagebus.domain.collector import EventCollector


class FileRepository(ItemRepository):
    IDENTIFIER = "FILE"

    def delete_items_of_folder(self, folder_uuid: UUID, org_pk: int | None) -> None:
        _org_id = org_pk if org_pk else 0

        files = EncryptedRecordDocument.objects.filter(
            folder_uuid=folder_uuid, org_id=_org_id
        )
        for file in files:
            file.delete_on_cloud()
        files.delete()


class EncryptedRecordDocument(FolderItemMixin, models.Model):
    REPOSITORY = "FILE"

    @classmethod
    def create(
        cls,
        file: UploadedFile,
        folder: Folder,
        by: OrgUser,
        collector: EventCollector,
        upload=False,
        pk=0,
    ) -> "EncryptedRecordDocument":
        name = "Unknown"
        if file.name:
            name = file.name
        f = EncryptedRecordDocument(org_id=folder.org_pk)
        if pk:
            f.pk = pk
        f.put_into_folder(folder, collector)
        f.set_name(name, collector)
        f.set_location()
        f.generate_key(by)
        if upload:
            f.upload(file, by)
        return f

    name = models.CharField(max_length=200)
    org = models.ForeignKey(Org, related_name="files", on_delete=models.CASCADE)
    uuid = models.UUIDField(db_index=True, unique=True, default=uuid4)
    folder_uuid = models.UUIDField(db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    file_size = models.BigIntegerField(null=True)
    location = models.SlugField(allow_unicode=True, max_length=1000, unique=True)
    exists = models.BooleanField(default=True)
    key = models.JSONField(null=True)

    if TYPE_CHECKING:
        org_id: int

    class Meta:
        verbose_name = "FIN_EncryptedRecordDocument"
        verbose_name_plural = "FIN_EncryptedRecordDocuments"

    def __str__(self):
        return "recordDocument: {}; name: {}; folderUuid: {};".format(
            self.pk, self.name, self.folder_uuid
        )

    @property
    def org_pk(self) -> int:
        assert self.org_id is not None
        return self.org_id

    @property
    def actions(self):
        return {}

    def set_name(self, name: str, collector: EventCollector):
        self.name = name
        self.renamed(collector)

    def generate_key(self, user: OrgUser):
        assert self.folder is not None and self.key is None
        key = SymmetricKey.generate(SymmetricEncryptionV1)
        lock_key = self.folder.get_encryption_key(requestor=user)
        enc_key = EncryptedSymmetricKey.create(key, lock_key)
        self.key = enc_key.as_dict()

    def set_location(self):
        assert self.location is None or self.location == ""
        self.location = "core/files_new/{}/{}".format(self.folder_uuid, uuid4())

    def __get_file_key(self):
        return "{}.enc".format(self.location)

    def __get_key(self, user: OrgUser):
        assert self.folder is not None

        decryption_key = self.folder.get_decryption_key(requestor=user)
        enc_key = EncryptedSymmetricKey.create_from_dict(self.key)
        key = enc_key.decrypt(decryption_key)

        return key.get_key()

    def upload(self, file: UploadedFile, by: OrgUser):
        key = self.__get_key(by)
        location = self.__get_file_key()
        encrypt_and_upload_file(file, location, key)

    def download(self, by: OrgUser):
        key = self.__get_key(by)
        location = self.__get_file_key()
        return download_and_decrypt_file(location, key)

    def delete_on_cloud(self):
        key = self.__get_file_key()
        default_storage.delete(key)
        self.exists = False

    def update_exists(self):
        key = self.__get_file_key()
        self.exists = default_storage.exists(key)
