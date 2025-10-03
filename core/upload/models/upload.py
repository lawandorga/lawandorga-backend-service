from tempfile import _TemporaryFileWrapper
from typing import IO, TYPE_CHECKING
from uuid import UUID, uuid4

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db import models

from core.auth.models import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.item import ItemRepository
from core.folders.domain.value_objects.asymmetric_key import (
    AsymmetricKey,
    EncryptedAsymmetricKey,
)
from core.folders.domain.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)
from core.folders.infrastructure.asymmetric_encryptions import AsymmetricEncryptionV1
from core.folders.infrastructure.item_mixins import FolderItemMixin
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1
from core.org.models import Org
from core.seedwork.domain_layer import DomainError
from core.seedwork.encryption import AESEncryption
from messagebus.domain.collector import EventCollector


class UploadLinkRepository(ItemRepository):
    IDENTIFIER = "UPLOAD"

    def delete_items_of_folder(self, folder_uuid: UUID, org_pk: int | None) -> None:
        _org_id = org_pk if org_pk else 0
        UploadLink.objects.filter(folder_uuid=folder_uuid, org_id=_org_id).delete()


class UploadLink(FolderItemMixin, models.Model):
    REPOSITORY = UploadLinkRepository.IDENTIFIER

    @staticmethod
    def create(
        name: str, folder: Folder, user: OrgUser, collector: EventCollector
    ) -> "UploadLink":
        link = UploadLink()
        link.org = user.org
        link.name = name
        link.put_into_folder(folder, collector)
        link.generate_key(user)
        return link

    name = models.CharField(max_length=200)
    org = models.ForeignKey(Org, on_delete=models.CASCADE)
    folder_uuid = models.UUIDField()
    uuid = models.UUIDField(default=uuid4)
    key = models.JSONField()
    disabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        files: models.QuerySet["UploadFile"]

    class Meta:
        verbose_name = "UPL_UploadLink"
        verbose_name_plural = "UPL_UploadLinks"

    @property
    def org_pk(self) -> int:
        return self.org.pk

    @property
    def enc_key(self) -> EncryptedAsymmetricKey:
        enc_key = EncryptedAsymmetricKey.create_from_dict(self.key)
        return enc_key

    @property
    def link(self) -> str:
        if self.disabled:
            return ""
        return f"{settings.MAIN_FRONTEND_URL}/uploads/{self.uuid}"

    @property
    def upload_files(self) -> dict[UUID, "UploadFile"]:
        if not hasattr(self, "_upload_files"):
            files = list(self.files.all())
            self._upload_files = {f.uuid: f for f in files}
        return self._upload_files

    @staticmethod
    def clean_up_storage() -> None:
        """
        This method should loop over the storage and look for files
        that are not connected anymore and delete them.
        """
        pass

    def generate_key(self, user: OrgUser):
        key = AsymmetricKey.generate(AsymmetricEncryptionV1)
        lock_key = self.folder.get_encryption_key(requestor=user)
        enc_key = EncryptedAsymmetricKey.create(key, lock_key)
        self.key = enc_key.as_dict()

    def disable(self):
        self.disabled = True

    def upload(self, name: str, f: UploadedFile) -> "UploadFile":
        if self.disabled:
            raise DomainError("This link is disabled. No more files can be uploaded.")

        file = UploadFile.create(name, self, f)

        if not hasattr(self, "_upload_files"):
            self._upload_files = {}
        self._upload_files[file.uuid] = file

        return file

    def download(
        self, uuid: UUID, user: OrgUser
    ) -> tuple[str, IO | _TemporaryFileWrapper]:
        file = self.upload_files[uuid]
        enc_key = EncryptedAsymmetricKey.create_from_dict(self.key)
        unlock_key = self.folder.get_decryption_key(requestor=user)
        key = enc_key.decrypt(unlock_key)
        return file.name, file.download(key)


def file_path(instance: "UploadFile", filename: str):
    return f"{UploadFile.UPLOAD_PATH}/{instance.link.folder_uuid}/${filename}"


class UploadFile(models.Model):
    UPLOAD_PATH = "core/upload"

    @staticmethod
    def create(name: str, link: UploadLink, f: UploadedFile) -> "UploadFile":
        file = UploadFile()
        file.link = link
        file.set_name(name)
        file.set_file(f)
        return file

    name = models.CharField(max_length=1000)
    uuid = models.UUIDField(default=uuid4)
    file = models.FileField(upload_to=file_path)
    link = models.ForeignKey(UploadLink, related_name="files", on_delete=models.CASCADE)
    key = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "UPL_UploadFile"
        verbose_name_plural = "UPL_UploadFiles"

    def generate_key(self):
        key = SymmetricKey.generate(SymmetricEncryptionV1)
        lock_key = self.link.enc_key
        enc_key = EncryptedSymmetricKey.create(key, lock_key)
        self.key = enc_key.as_dict()
        return key

    def get_key(self, unlock_key: AsymmetricKey) -> SymmetricKey:
        enc_key = EncryptedSymmetricKey.create_from_dict(self.key)
        key = enc_key.decrypt(unlock_key)
        return key

    def set_name(self, name: str):
        if "." not in name:
            raise DomainError(
                "The filename needs to have an extension like '.pdf' or '.txt'."
            )
        if len(name.split(".")[0]) == 0 or len(name.split(".")[1]) == 0:
            raise DomainError(
                "The filename needs to have a name and "
                "an extension for example 'sample.pdf'."
            )

        self.name = name

    def set_file(self, file: UploadedFile):
        if file.name is None or "." not in file.name:
            raise DomainError("The filename is not correct.")

        if self.name.split(".")[-1] != file.name.split(".")[-1]:
            raise DomainError(
                "The filename needs to end with '.{}'.".format(file.name.split(".")[-1])
            )

        file_name = f"{uuid4()}.enc"

        key = self.generate_key()
        enc_f = AESEncryption.encrypt_in_memory_file(
            file, key.get_key().decode("utf-8")
        )
        self.file.save(file_name, enc_f, save=False)

    def download(self, link_key: AsymmetricKey) -> IO | _TemporaryFileWrapper:
        key = self.get_key(link_key)
        f = AESEncryption.decrypt_bytes_file(
            self.file.file, key.get_key().decode("utf-8")
        )
        return f

    def delete_file(self):
        self.file.delete(save=False)
