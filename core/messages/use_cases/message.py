from uuid import UUID

from core.auth.models import OrgUser
from core.folders.usecases.finders import folder_from_uuid
from core.messages.models import EncryptedRecordMessage
from core.messages.use_cases.finders import get_message_by_uuid
from core.seedwork.use_case_layer import use_case


@use_case
def create_a_message(__actor: OrgUser, message: str, folder_uuid: UUID):
    folder = folder_from_uuid(__actor, folder_uuid)

    m = EncryptedRecordMessage.create(
        sender=__actor, folder_uuid=folder.uuid, message=message
    )
    m.encrypt(user=__actor)
    m.save()


@use_case
def delete_message(__actor: OrgUser, message_id: int):
    message = get_message_by_uuid(__actor, message_id)
    message.delete()


@use_case
def optimize_messages(__actor: OrgUser):
    pass
