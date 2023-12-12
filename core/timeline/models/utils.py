from uuid import UUID

from django.db import models

from core.auth.models.org_user import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.value_objects.box import LockedBox, OpenBox


class EncryptDecryptMethods:
    folder_uuid: UUID | models.UUIDField
    ENCRYPTED_FIELDS: list[str]

    def encrypt(self, folder: Folder, user: OrgUser) -> None:
        assert folder.uuid == self.folder_uuid, "folder uuid mismatch"
        key = folder.get_encryption_key(requestor=user)
        for field in self.ENCRYPTED_FIELDS:
            value: str = getattr(self, field)
            box = OpenBox(value.encode("utf-8"))
            if value is not None:
                setattr(self, "{}_enc".format(field), key.lock(box).as_dict())
        self.is_encrypted = True

    def decrypt(self, folder: Folder, user: OrgUser) -> None:
        assert folder.uuid == self.folder_uuid, "folder uuid mismatch"
        key = folder.get_decryption_key(requestor=user)
        for field in self.ENCRYPTED_FIELDS:
            value: dict = getattr(self, "{}_enc".format(field))
            if value is not None:
                locked_box = LockedBox.create_from_dict(value)
                box = key.unlock(locked_box)
                setattr(self, field, box.value_as_str)
        self.is_encrypted = False
