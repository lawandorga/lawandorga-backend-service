from typing import TYPE_CHECKING, Optional, Protocol

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.aggregates.item import FolderItem, Item
from core.folders.domain.value_objects.encryption import EncryptionDecryptionError
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.seedwork.aggregate import Addon
from core.seedwork.events_addon import EventsAddon

if TYPE_CHECKING:
    from core.auth.models.org_user import OrgUser


class Object(Item, Protocol):
    events: EventsAddon


class FolderAddon(Addon):
    def __init__(self, obj: Object):
        super().__init__(obj)
        self._folder: Optional[Folder] = None

    @property
    def folder(self) -> Folder:
        assert self._obj.folder_uuid is not None
        if not hasattr(self, "_folder") or getattr(self, "_folder", None) is None:
            r = DjangoFolderRepository()
            self._folder = r.retrieve(self._obj.org_pk, self._obj.folder_uuid)
        assert self._folder is not None
        return self._folder

    def get_decryption_key(self, requestor: "OrgUser"):
        try:
            return self.folder.get_decryption_key(requestor=requestor)
        except EncryptionDecryptionError as e:
            folder = self.folder.get_folder_of_access(requestor)
            if folder is not None:
                folder.invalidate_keys_of(requestor)
                r = DjangoFolderRepository()
                r.save(folder)
            raise e

    def get_encryption_key(self, requestor: "OrgUser"):
        return self.folder.get_encryption_key(requestor=requestor)

    def has_access(self, user: "OrgUser"):
        return self.folder.has_access(user)

    def put_obj_in_folder(self, folder: Folder):
        assert self._obj.folder_uuid is None
        self._obj.folder_uuid = folder.uuid
        self._folder = folder
        self.obj_placed()

    def obj_placed(self):
        self._obj.events.add(
            FolderItem.ItemAddedToFolder(
                org_pk=self._obj.org_pk,
                uuid=self._obj.uuid,
                repository=self._obj.REPOSITORY,
                name=self._obj.name,
                folder_uuid=self._obj.folder_uuid,
            )
        )

    def obj_renamed(self):
        self._obj.events.add(
            FolderItem.ItemRenamed(
                org_pk=self._obj.org_pk,
                uuid=self._obj.uuid,
                repository=self._obj.REPOSITORY,
                name=self._obj.name,
                folder_uuid=self._obj.folder_uuid,
            )
        )

    def obj_deleted(self):
        if self._obj.folder_uuid:
            self._obj.events.add(
                FolderItem.ItemDeleted(
                    org_pk=self._obj.org_pk,
                    uuid=self._obj.uuid,
                    repository=self._obj.REPOSITORY,
                    name=self._obj.name,
                    folder_uuid=self._obj.folder_uuid,
                )
            )

    pre_delete = [obj_deleted]
