from core.auth.models import RlcUser
from core.folders.domain.aggregates.item import FolderItem
from core.folders.use_cases.folder import (
    add_item_to_folder,
    correct_keys_of_user_by_user,
    delete_item_from_folder,
    invalidate_keys_of_user,
    rename_item_in_folder,
)
from core.seedwork.message_layer import MessageBusActor
from messagebus import MessageBus


@MessageBus.handler(on=FolderItem.ItemRenamed)
def handler__item_renamed(event: FolderItem.ItemRenamed):
    rename_item_in_folder(
        MessageBusActor(event.org_pk),
        event.repository,
        event.uuid,
        event.folder_uuid,
    )


@MessageBus.handler(on=FolderItem.ItemDeleted)
def handler__item_deleted(event: FolderItem.ItemDeleted):
    delete_item_from_folder(
        MessageBusActor(event.org_pk),
        event.uuid,
        event.folder_uuid,
    )


@MessageBus.handler(on=FolderItem.ItemAddedToFolder)
def handler__item_added_to_folder(event: FolderItem.ItemAddedToFolder):
    add_item_to_folder(
        MessageBusActor(event.org_pk),
        event.repository,
        event.uuid,
        event.folder_uuid,
    )


@MessageBus.handler(on=RlcUser.OrgUserLocked)
def handler__org_user_locked(event: RlcUser.OrgUserLocked):
    invalidate_keys_of_user(MessageBusActor(event.org_pk), event.org_user_uuid)


@MessageBus.handler(on=RlcUser.OrgUserUnlocked)
def handler__org_user_unlocked(event: RlcUser.OrgUserUnlocked):
    of_uuid = event.org_user_uuid
    by_uuid = event.by_org_user_uuid
    correct_keys_of_user_by_user(MessageBusActor(event.org_pk), of_uuid, by_uuid)
