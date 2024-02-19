from typing import TYPE_CHECKING, Optional
from uuid import UUID

from django.db import models

from core.auth.models import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1
from core.rlc.models import Org
from core.seedwork.encryption import AESEncryption


class EncryptedRecordMessage(models.Model):
    @classmethod
    def create(
        cls, sender: OrgUser, folder_uuid: UUID, message: str
    ) -> "EncryptedRecordMessage":
        m = EncryptedRecordMessage(
            sender=sender, org_id=sender.org_id, folder_uuid=folder_uuid
        )
        m.message = message
        return m

    sender = models.ForeignKey(
        OrgUser,
        related_name="messages",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    org = models.ForeignKey(Org, related_name="messages", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    folder_uuid = models.UUIDField()

    key = models.JSONField()
    enc_message = models.JSONField()

    encryption_class = AESEncryption
    encrypted_fields = ["message"]

    if TYPE_CHECKING:
        objects: models.Manager["EncryptedRecordMessage"]
        org_id: int

    class Meta:
        ordering = ["created"]
        verbose_name = "RecordMessage"
        verbose_name_plural = "RecordMessages"

    def __str__(self):
        return "recordMessage: {}; folder: {};".format(self.pk, self.folder_uuid)

    @property
    def folder(self) -> Optional[Folder]:
        assert self.folder_uuid is not None
        if not hasattr(self, "_folder"):
            r = DjangoFolderRepository()
            self._folder = r.retrieve(self.org_id, self.folder_uuid)
        return self._folder

    @property
    def sender_name(self):
        if self.sender:
            return self.sender.name
        return "Deleted"

    def encrypt(self, user: OrgUser):
        assert self.folder_uuid is not None

        self.__generate_key(user)
        key = self.get_key(user)
        open_box = OpenBox(data=self.message.encode("utf-8"))
        locked_box = key.lock(open_box)
        self.enc_message = locked_box.as_dict()

    def decrypt(self, user: OrgUser) -> "EncryptedRecordMessage":
        assert self.folder_uuid is not None

        key = self.get_key(user)
        locked_box = LockedBox.create_from_dict(self.enc_message)
        open_box = key.unlock(locked_box)
        self.message = open_box.decode("utf-8")
        return self

    def __generate_key(self, user: OrgUser):
        assert self.folder is not None

        key = SymmetricKey.generate(SymmetricEncryptionV1)
        lock_key = self.folder.get_encryption_key(requestor=user)
        enc_key = EncryptedSymmetricKey.create(key, lock_key)
        self.key = enc_key.as_dict()

    def get_key(self, user: OrgUser) -> SymmetricKey:
        assert self.folder is not None

        enc_key = EncryptedSymmetricKey.create_from_dict(self.key)
        unlock_key = self.folder.get_decryption_key(requestor=user)
        key = enc_key.decrypt(unlock_key)
        return key
