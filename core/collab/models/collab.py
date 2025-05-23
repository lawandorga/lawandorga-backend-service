from typing import TYPE_CHECKING
from uuid import uuid4

from django.db import models
from django.utils import timezone

from core.auth.models.org_user import OrgUser
from core.collab.models.template import Template
from core.collab.value_objects.document import Document, EncryptedDocument
from core.folders.domain.aggregates.folder import Folder
from core.folders.infrastructure.item_mixins import FolderItemMixin
from core.org.models.org import Org
from messagebus.domain.collector import EventCollector


class Collab(FolderItemMixin, models.Model):
    REPOSITORY: str = "COLLAB"

    @classmethod
    def create(
        cls, user: OrgUser, title: str, folder: Folder, collector: EventCollector
    ) -> "Collab":
        collab = Collab(
            org=user.org,
            uuid=uuid4(),
            title=title,
        )
        doc = Document.create(user=cls.create_doc_user(user), text="")
        collab.put_into_folder(folder, collector)
        collab.history = [doc]
        return collab

    @classmethod
    def create_doc_user(cls, user: OrgUser) -> str:
        return f"{user.name} ({user.email})"

    org = models.ForeignKey(Org, on_delete=models.CASCADE, related_name="collabs")
    uuid = models.UUIDField(unique=True, default=uuid4)
    title = models.CharField(max_length=256)
    folder_uuid = models.UUIDField()
    history_enc = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history: list[Document]
    objects = models.Manager()
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True)

    if TYPE_CHECKING:
        org_id: int

    class Meta:
        verbose_name = "COL_Collab"
        verbose_name_plural = "COL_Collabs"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if "__allow" not in kwargs:
            raise ValueError("only the repository should save this model")
        kwargs.pop("__allow")
        return super().save(*args, **kwargs)

    @property
    def org_pk(self) -> int:
        return self.org_id

    @property
    def name(self) -> str:  # type: ignore
        return self.title

    @property
    def text(self) -> str:
        return self.history[-1].text

    @property
    def password(self) -> str:
        today_date = timezone.now().strftime("%Y-%m-%d")
        uuid = self.uuid
        text = f"{today_date}{uuid}"
        return str(hash(text))

    def sync(self, text: str, user: OrgUser) -> None:
        doc = Document.create(user=self.create_doc_user(user), text=text)
        self.history.append(doc)

    def update_title(self, title: str, collector: EventCollector) -> None:
        self.title = title
        self.renamed(collector)

    def update_template(self, template: Template | None) -> None:
        self.template = template

    def _encrypt(self, folder: Folder, user: OrgUser) -> None:
        enc_history_uuids = [d["uuid"] for d in self.history_enc]
        key = folder.get_encryption_key(requestor=user)
        for d in self.history:
            if str(d.uuid) not in enc_history_uuids:
                enc_doc = EncryptedDocument.create_from_document(d, key)
                self.history_enc.append(enc_doc.as_dict())

    def _decrypt(self, folder: Folder, user: OrgUser) -> None:
        self.history = []
        for d in self.history_enc:
            enc_doc = EncryptedDocument.create_from_dict(d)
            key = folder.get_decryption_key(requestor=user)
            doc = enc_doc.decrypt(key)
            self.history.append(doc)
