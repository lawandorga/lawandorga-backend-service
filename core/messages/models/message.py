from typing import TYPE_CHECKING, Optional, cast
from uuid import UUID

from django.db import models

from core.auth.models import RlcUser
from core.data_sheets.models.data_sheet import DataSheet
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.folder import FolderRepository
from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)
from core.rlc.models import Org
from core.seedwork.encryption import AESEncryption
from core.seedwork.repository import RepositoryWarehouse


class EncryptedRecordMessage(models.Model):
    @classmethod
    def create(
        cls, sender: RlcUser, folder_uuid: UUID, message: str
    ) -> "EncryptedRecordMessage":
        m = EncryptedRecordMessage(
            sender=sender, org_id=sender.org_id, folder_uuid=folder_uuid
        )
        m.message = message
        return m

    sender = models.ForeignKey(
        RlcUser,
        related_name="messages",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    record = models.ForeignKey(
        DataSheet, related_name="messages", on_delete=models.CASCADE, null=True
    )
    org = models.ForeignKey(Org, related_name="messages", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    folder_uuid = models.UUIDField(null=True)

    key = models.JSONField(null=True)
    # encrypted
    message: str = models.BinaryField(null=False)  # type: ignore
    enc_message = models.JSONField(null=True)

    encryption_class = AESEncryption
    encrypted_fields = ["message"]

    if TYPE_CHECKING:
        objects: models.Manager["EncryptedRecordMessage"]

    class Meta:
        ordering = ["created"]
        verbose_name = "RecordMessage"
        verbose_name_plural = "RecordMessages"

    def __str__(self):
        return "recordMessage: {}; record: {};".format(self.pk, self.record.pk)

    @property
    def folder(self) -> Optional[Folder]:
        assert self.folder_uuid is not None
        if not hasattr(self, "_folder"):
            r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
            self._folder = r.retrieve(self.org_id, self.folder_uuid)  # type: ignore
        return self._folder

    @property
    def sender_name(self):
        if self.sender:
            return self.sender.name
        return "Deleted"

    def save(self, *args, **kwargs):
        self.message = b""
        super().save(*args, **kwargs)

    def encrypt(self, user: RlcUser):
        assert self.folder_uuid is not None

        self.__generate_key(user)
        key = self.get_key(user)
        open_box = OpenBox(data=self.message.encode("utf-8"))
        locked_box = key.lock(open_box)
        self.enc_message = locked_box.as_dict()

    def decrypt(self, user: RlcUser) -> "EncryptedRecordMessage":
        assert self.folder_uuid is not None

        key = self.get_key(user)
        locked_box = LockedBox.create_from_dict(self.enc_message)
        open_box = key.unlock(locked_box)
        self.message = open_box.decode("utf-8")
        return self

    def __decrypt_old(self, user: RlcUser):
        key = self.record.get_aes_key(user)
        return self.encryption_class.decrypt(self.message, key)  # type: ignore

    def __generate_key(self, user: RlcUser):
        assert self.folder is not None

        key = SymmetricKey.generate()
        lock_key = self.folder.get_encryption_key(requestor=user)
        enc_key = EncryptedSymmetricKey.create(key, lock_key)
        self.key = enc_key.as_dict()

    def get_key(self, user: RlcUser) -> SymmetricKey:
        assert self.folder is not None

        enc_key = EncryptedSymmetricKey.create_from_dict(self.key)
        unlock_key = self.folder.get_decryption_key(requestor=user)
        key = enc_key.decrypt(unlock_key)
        return key

    def put_in_folder(self, user: RlcUser):
        if not self.record.folder_uuid or not self.record.folder.has_access(user):
            return

        message = self.__decrypt_old(user)
        box = OpenBox(data=message.encode("utf-8"))
        self.folder_uuid = self.record.folder_uuid
        self.__generate_key(user)
        key = self.get_key(user)
        locked_box = key.lock(box)
        self.enc_message = locked_box.as_dict()
