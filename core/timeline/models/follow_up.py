from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from django.db import models

from core.auth.models.org_user import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.rlc.models.org import Org
from core.timeline.models.utils import EncryptDecryptMethods


class TimelineFollowUp(EncryptDecryptMethods, models.Model):
    @classmethod
    def create(
        cls, folder: Folder, user: RlcUser, title: str, text: str, time: datetime
    ) -> "TimelineFollowUp":
        follow_up = TimelineFollowUp(
            org=user.org,
            uuid=uuid4(),
            time=time,
            folder_uuid=folder.uuid,
        )
        follow_up.title = title
        follow_up.text = text
        return follow_up

    uuid = models.UUIDField(primary_key=True)
    text_enc = models.JSONField(default=dict)
    title_enc = models.JSONField(default=dict)
    time = models.DateTimeField()
    folder_uuid = models.UUIDField()
    is_done = models.BooleanField(default=False)
    org = models.ForeignKey(
        Org, on_delete=models.CASCADE, related_name="timeline_follow_ups"
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
        return "follow_up"

    def save(self, *args, **kwargs):
        if not self.is_encrypted:
            raise ValueError("cannot save unencrypted timeline follow up")
        return super().save(*args, **kwargs)

    def update(
        self,
        title: str | None,
        text: str | None,
        time: datetime | None,
        is_done: bool | None,
    ) -> None:
        if title is not None:
            self.title = title
        if text is not None:
            self.text = text
        if time is not None:
            self.time = time
        if is_done is not None:
            self.is_done = is_done

    def set_done(self):
        self.is_done = True
