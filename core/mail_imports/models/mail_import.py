import logging
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from django.db import models
from django.utils.timezone import localtime

from core.auth.models.org_user import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.value_objects.box import LockedBox, OpenBox
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
    def create(
        cls,
        sender: str,
        to: str,
        subject: str,
        content: str,
        folder_uuid: UUID,
        org_id: int,
        bcc: str = "",
        sending_datetime: str | None = None,
    ):
        mi = cls(
            sender=sender,
            to=to,
            folder_uuid=folder_uuid,
            org_id=org_id,
            bcc=bcc,
        )
        if sending_datetime:
            mi.sending_datetime = sending_datetime
        mi.subject = subject
        mi.content = content
        return mi

    org = models.ForeignKey(Org, on_delete=models.CASCADE, related_name="mail_imports")
    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True, editable=False)
    sender = models.CharField(max_length=255, blank=False)
    to = models.CharField(max_length=255, blank=False)
    cc = models.CharField(max_length=255, blank=True)
    bcc = models.CharField(max_length=255, blank=True)
    sending_datetime = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    folder_uuid = models.UUIDField(db_index=True)
    # encrypted content
    ENC_FIELDS = ["subject", "content"]
    enc_subject = models.JSONField()
    enc_content = models.JSONField()
    enc_key = models.JSONField()

    if TYPE_CHECKING:
        org_id: int
        subject: str
        content: str

    class Meta:
        verbose_name = "MI_MailImport"
        verbose_name_plural = "MI_MailImports"

    @property
    def folder(self) -> Folder:
        if not hasattr(self, "_folder"):
            r = DjangoFolderRepository()
            self._folder = r.retrieve(self.org_id, self.folder_uuid)
        return self._folder

    def __str__(self) -> str:
        time = localtime(self.sending_datetime).strftime("%Y-%m-%d %H:%M:%S")
        return f"mailImport: {self.folder_uuid}; time: {time};"

    def mark_as_read(self):
        self.is_read = True

    def mark_as_unread(self):
        self.is_read = False

    def toggle_pinned(self):
        self.is_pinned = not self.is_pinned

    def encrypt(self, user: OrgUser):
        self.__generate_key(user)
        key = self.get_key(user)
        for field in self.ENC_FIELDS:
            value = getattr(self, field, "")
            open_box = OpenBox(data=value.encode("utf-8"))
            locked_box = key.lock(open_box)
            setattr(self, f"enc_{field}", locked_box.as_dict())

    def decrypt(self, user: OrgUser):
        key = self.get_key(user)
        for field in self.ENC_FIELDS:
            locked_box = LockedBox.create_from_dict(getattr(self, f"enc_{field}"))
            open_box = key.unlock(locked_box)
            setattr(self, field, open_box.value_as_str)

    def __generate_key(self, user: OrgUser):
        key = SymmetricKey.generate(SymmetricEncryptionV1)
        lock_key = self.folder.get_encryption_key(requestor=user)
        enc_key = EncryptedSymmetricKey.create(key, lock_key)
        self.enc_key = enc_key.as_dict()

    def get_key(self, user: OrgUser) -> SymmetricKey:
        enc_key = EncryptedSymmetricKey.create_from_dict(self.enc_key)
        unlock_key = self.folder.get_decryption_key(requestor=user)
        key = enc_key.decrypt(unlock_key)
        return key


class MailAttachement(models.Model):
    @classmethod
    def create(
        cls,
        mail_import: MailImport,
    ):
        attachment = cls(
            mail_import=mail_import,
            file_name="",
            file_location="",
        )
        return attachment

    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True, editable=False)
    mail_import = models.ForeignKey(
        MailImport, on_delete=models.CASCADE, related_name="attachements"
    )
    file_name = models.CharField(max_length=255)
    file_location = models.SlugField(allow_unicode=True, max_length=1000, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "MI_MailAttachment"
        verbose_name_plural = "MI_MailAttachments"

    def __str__(self) -> str:
        mail_import_uuid = self.mail_import.folder_uuid
        return f"mailAttachment: {self.uuid}; mailImportUUid: {mail_import_uuid}"

    def upload_file(self, file):
        raise NotImplementedError()
