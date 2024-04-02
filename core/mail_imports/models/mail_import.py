import logging
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from django.db import models
from django.utils.timezone import localtime

from core.auth.models.org_user import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1
from core.rlc.models.org import Org

logger = logging.getLogger("django")


class MailImport(models.Model):
    @classmethod
    def create(cls, sender: str, subject: str, content: str, folder_uuid: UUID):
        return cls(
            sender=sender,
            subject=subject,
            content=content,
            folder_uuid=folder_uuid,
        )

    org = models.ForeignKey(Org, on_delete=models.CASCADE, related_name="mail_imports")
    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True, editable=False)
    sender = models.CharField(max_length=255, blank=False)
    cc = models.CharField(max_length=255, blank=True)
    bcc = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    content = models.TextField(max_length=255, blank=True)
    sending_datetime = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    folder_uuid = models.UUIDField(db_index=True)

    if TYPE_CHECKING:
        org_id: int

    class Meta:
        verbose_name = "MI_MailImport"
        verbose_name_plural = "MI_MailImports"

    @property
    def folder(self) -> Folder:
        assert self.folder_uuid is not None
        if not hasattr(self, "_folder"):
            r = DjangoFolderRepository()
            self._folder = r.retrieve(self.org_id, self.folder_uuid)
        return self._folder

    def __str__(self) -> str:
        time = localtime(self.sending_datetime).strftime("%Y-%m-%d %H:%M:%S")
        return f"mailImport: {self.folder_uuid}; time: {time};"

    def mark_as_read(self):
        self.is_read = True

    def toggle_pinned(self):
        self.is_pinned = not self.is_pinned

    def encrypt(self, user: OrgUser):
        raise NotImplementedError("where to get the asymmetric key?")
        # assert self.folder_uuid is not None

        # self.__generate_key(user)
        # key = self.get_key(user)
        # open_box = OpenBox(data=self.content.encode("utf-8"))
        # locked_box = key.lock(open_box)
        # self.enc_content = locked_box.as_dict()

    def decrypt(self):
        raise NotImplementedError()

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
