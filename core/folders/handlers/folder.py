from core.auth.models import OrgUser
from core.folders.domain.aggregates.item import FolderItem
from core.folders.usecases.folder import (
    add_item_to_folder,
    correct_keys_of_user_by_user,
    delete_item_from_folder,
    invalidate_keys_of_user,
    rename_item_in_folder,
)
from core.seedwork.message_layer import MessageBusActor


def handler__item_renamed(event: FolderItem.ItemRenamed):
    rename_item_in_folder(
        MessageBusActor(event.org_pk),
        event.repository,
        event.name,
        event.uuid,
        event.folder_uuid,
    )


def handler__item_deleted(event: FolderItem.ItemDeleted):
    delete_item_from_folder(
        MessageBusActor(event.org_pk),
        event.uuid,
        event.folder_uuid,
    )


def handler__item_added_to_folder(event: FolderItem.ItemAddedToFolder):
    add_item_to_folder(
        MessageBusActor(event.org_pk),
        event.repository,
        event.name,
        event.uuid,
        event.folder_uuid,
    )


def handler__org_user_locked(event: OrgUser.OrgUserLocked):
    invalidate_keys_of_user(MessageBusActor(event.org_pk), event.uuid)


def handler__org_user_unlocked(event: OrgUser.OrgUserUnlocked):
    of_uuid = event.uuid
    by_uuid = event.by_org_user_uuid
    correct_keys_of_user_by_user(MessageBusActor(event.org_pk), of_uuid, by_uuid)
