from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from django.db import models

from core.auth.models.org_user import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.value_objects.box import LockedBox, OpenBox


class TimelineFollowUp(models.Model):
    @classmethod
    def create(
        cls, folder: Folder, user: RlcUser, title: str, text: str, time: datetime
    ) -> "TimelineFollowUp":
        follow_up = TimelineFollowUp(
            org=user.org,
            uuid=uuid4(),
            time=time,
            created_by=user,
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
    org = models.ForeignKey(
        "auth.Org", on_delete=models.CASCADE, related_name="timeline_follow_ups"
    )
    created_by = models.ForeignKey(
        "auth.RlcUser",
        on_delete=models.SET_NULL,
        related_name="timeline_follow_ups",
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    ENCRYPTED_FIELDS = ["title", "text"]

    if TYPE_CHECKING:
        title: str
        text: str
        is_encrypted: bool

    def save(self, *args, **kwargs):
        if not self.is_encrypted:
            raise ValueError("cannot save unencrypted timeline follow up")
        return super().save(*args, **kwargs)

    def encrypt(self, folder: Folder, user: RlcUser) -> None:
        assert folder.uuid == self.folder_uuid, "folder uuid mismatch"
        key = folder.get_encryption_key(requestor=user)
        for field in self.ENCRYPTED_FIELDS:
            value: str = getattr(self, field)
            box = OpenBox(value.encode("utf-8"))
            if value is not None:
                setattr(self, "{}_enc".format(field), key.lock(box).as_dict())
        self.is_encrypted = True

    def decrypt(self, folder: Folder, user: RlcUser) -> None:
        assert folder.uuid == self.folder_uuid, "folder uuid mismatch"
        key = folder.get_decryption_key(requestor=user)
        for field in self.ENCRYPTED_FIELDS:
            value: dict = getattr(self, "{}_enc".format(field))
            if value is not None:
                locked_box = LockedBox.create_from_dict(value)
                box = key.unlock(locked_box)
                setattr(self, field, box.value_as_str)
        self.is_encrypted = False
