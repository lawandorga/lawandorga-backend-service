from uuid import UUID

from core.auth.models import OrgUser
from core.data_sheets.use_cases.finders import find_record_from_folder_uuid
from core.folders.use_cases.finders import folder_from_uuid
from core.messages.models import EncryptedRecordMessage
from core.messages.use_cases.finders import get_message_by_uuid
from core.seedwork.use_case_layer import use_case


def update_record_updated_at(__actor: OrgUser, folder_uuid: UUID):
    record = find_record_from_folder_uuid(__actor, folder_uuid)
    if not record:
        return
    record.update_timestamps()
    record.save()


@use_case
def create_a_message(__actor: OrgUser, message: str, folder_uuid: UUID):
    folder = folder_from_uuid(__actor, folder_uuid)

    m = EncryptedRecordMessage.create(
        sender=__actor, folder_uuid=folder.uuid, message=message
    )
    m.encrypt(user=__actor)
    m.save()
    update_record_updated_at(__actor, folder.uuid)


@use_case
def delete_message(__actor: OrgUser, message_id: int):
    message = get_message_by_uuid(__actor, message_id)
    folder_uuid = message.folder_uuid
    message.delete()
    update_record_updated_at(__actor, folder_uuid)
