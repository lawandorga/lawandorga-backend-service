from core.messages.models import EncryptedRecordMessage
from core.messages.use_cases.message import create_a_message, delete_message
from core.tests import test_helpers


def test_create_message_updates_related_record_timestamp(db):
    data = test_helpers.create_record()
    record = data["record"]
    user = data["user"]

    previous_updated = record.updated

    create_a_message(
        __actor=user,
        message="Bitte pruefe den aktuellen Stand.",
        folder_uuid=record.folder_uuid,
    )

    record.refresh_from_db()
    assert (
        EncryptedRecordMessage.objects.filter(folder_uuid=record.folder_uuid).count()
        == 1
    )
    assert record.updated > previous_updated


def test_delete_message_updates_related_record_timestamp(db):
    data = test_helpers.create_record()
    record = data["record"]
    user = data["user"]

    create_a_message(
        __actor=user,
        message="Bitte loeschen.",
        folder_uuid=record.folder_uuid,
    )
    message_id = EncryptedRecordMessage.objects.values_list("id", flat=True).get(
        folder_uuid=record.folder_uuid
    )

    record.refresh_from_db()
    previous_updated = record.updated

    delete_message(__actor=user, message_id=message_id)

    record.refresh_from_db()
    assert (
        EncryptedRecordMessage.objects.filter(folder_uuid=record.folder_uuid).count()
        == 0
    )
    assert record.updated > previous_updated
