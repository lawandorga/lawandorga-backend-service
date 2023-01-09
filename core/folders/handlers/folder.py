from core.auth.models import OrgUserLocked, OrgUserUnlocked
from core.folders.domain.aggregates.item import (
    ItemAddedToFolder,
    ItemDeleted,
    ItemRenamed,
)
from core.folders.use_cases.folder import (
    add_item_to_folder,
    correct_keys_of_user_by_user,
    delete_item_from_folder,
    invalidate_keys_of_user,
    rename_item_in_folder,
)
from core.seedwork.message_layer import MessageBusActor
from messagebus import Event, MessageBus


@MessageBus.handler(on=ItemRenamed)
def handler__item_renamed(event: Event[ItemRenamed]):
    rename_item_in_folder(
        MessageBusActor(event.data.org_pk),
        event.data.repository,
        event.data.uuid,
        event.data.folder_uuid,
    )


@MessageBus.handler(on=ItemDeleted)
def handler__item_deleted(event: Event[ItemDeleted]):
    delete_item_from_folder(
        MessageBusActor(event.data.org_pk),
        event.data.uuid,
        event.data.folder_uuid,
    )


@MessageBus.handler(on=ItemAddedToFolder)
def handler__item_added_to_folder(event: Event[ItemAddedToFolder]):
    add_item_to_folder(
        MessageBusActor(event.data.org_pk),
        event.data.repository,
        event.data.uuid,
        event.data.folder_uuid,
    )


@MessageBus.handler(on=OrgUserLocked)
def handler__org_user_locked(event: Event[OrgUserLocked]):
    invalidate_keys_of_user(
        MessageBusActor(event.data.org_pk), event.data.org_user_uuid
    )


@MessageBus.handler(on=OrgUserUnlocked)
def handler__org_user_unlocked(event: Event[OrgUserUnlocked]):
    of_uuid = event.data.org_user_uuid
    by_uuid = event.data.by_org_user_uuid
    correct_keys_of_user_by_user(MessageBusActor(event.data.org_pk), of_uuid, by_uuid)
