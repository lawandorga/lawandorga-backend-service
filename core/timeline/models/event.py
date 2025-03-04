from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from django.db import models

from core.auth.models.org_user import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.org.models.org import Org
from core.timeline.models.utils import EncryptDecryptMethods


class TimelineEvent(EncryptDecryptMethods, models.Model):
    @classmethod
    def create(
        cls, folder: Folder, user: OrgUser, title: str, text: str, time: datetime
    ) -> "TimelineEvent":
        event = TimelineEvent(
            org=user.org,
            uuid=uuid4(),
            time=time,
            folder_uuid=folder.uuid,
        )
        event.title = title
        event.text = text
        return event

    uuid = models.UUIDField(primary_key=True)
    text_enc = models.JSONField(default=dict)
    title_enc = models.JSONField(default=dict)
    time = models.DateTimeField()
    folder_uuid = models.UUIDField()
    org = models.ForeignKey(
        Org, on_delete=models.CASCADE, related_name="timeline_events"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    ENCRYPTED_FIELDS = ["title", "text"]

    if TYPE_CHECKING:
        title: str
        text: str
        is_encrypted: bool

    @property
    def type(self) -> str:
        return "event"

    def save(self, *args, **kwargs):
        if not self.is_encrypted:
            raise ValueError("cannot save unencrypted timeline follow up")
        return super().save(*args, **kwargs)

    def update(
        self, title: str | None, text: str | None, time: datetime | None
    ) -> None:
        if title is not None:
            self.title = title
        if text is not None:
            self.text = text
        if time is not None:
            self.time = time
