from typing import Optional
from uuid import UUID, uuid4

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.db import models

from core.auth.models import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.item import ItemRepository
from core.folders.domain.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)
from core.folders.infrastructure.folder_addon import FolderAddon
from core.records.models.record import Record
from core.rlc.models import Org
from core.seedwork.aggregate import Aggregate
from core.seedwork.events_addon import EventsAddon
from core.seedwork.storage import download_and_decrypt_file, encrypt_and_upload_file


class DjangoFileRepository(ItemRepository):
    IDENTIFIER = "FILE"

    @classmethod
    def retrieve(
        cls, uuid: UUID, org_pk: Optional[int] = None
    ) -> "EncryptedRecordDocument":
        assert isinstance(uuid, UUID)
        return EncryptedRecordDocument.objects.get(uuid=uuid)


class EncryptedRecordDocument(Aggregate, models.Model):
    REPOSITORY = "FILE"

    @classmethod
    def create(
        cls, file: UploadedFile, folder: Folder, by: RlcUser, upload=False, pk=0
    ) -> "EncryptedRecordDocument":
        name = "Unknown"
        if file.name:
            name = file.name
        f = EncryptedRecordDocument(org_id=folder.org_pk)
        if pk:
            f.pk = pk
        f.folder.put_obj_in_folder(folder)
        f.set_name(name)
        f.set_location()
        f.generate_key(by)
        if upload:
            f.upload(file, by)
        return f

    name = models.CharField(max_length=200)
    record: Optional[Record] = models.ForeignKey(  # type: ignore
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

    addons = dict(events=EventsAddon, folder=FolderAddon)
    events: EventsAddon
    folder: FolderAddon

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

    # @property
    # def folder(self) -> Optional[Folder]:
    #     assert self.org_id is not None
    #     if self.folder_uuid is None:
    #         return None
    #     if not hasattr(self, "_folder"):
    #         r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    #         self._folder = r.retrieve(self.org_id, self.folder_uuid)
    #     return self._folder

    @property
    def actions(self):
        return {}

    def set_name(self, name: str):
        self.name = name
        self.folder.obj_renamed()

    def generate_key(self, user: RlcUser):
        assert self.folder is not None and self.key is None
        key = SymmetricKey.generate()
        lock_key = self.folder.get_encryption_key(requestor=user)
        enc_key = EncryptedSymmetricKey.create(key, lock_key)
        self.key = enc_key.as_dict()

    def set_location(self):
        assert self.location is None or self.location == ""
        self.location = "core/files_new/{}/{}".format(self.folder_uuid, uuid4())

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
        self.exists = False

    def update_exists(self):
        key = self.__get_file_key()
        self.exists = default_storage.exists(key)
