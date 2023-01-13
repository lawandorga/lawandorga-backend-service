from uuid import UUID

from core.auth.models import RlcUser
from core.folders.use_cases.finders import folder_from_uuid
from core.messages.models import EncryptedRecordMessage
from core.seedwork.use_case_layer import use_case


@use_case
def create_a_message(__actor: RlcUser, message: str, folder_uuid: UUID):
    folder = folder_from_uuid(__actor, folder_uuid)

    m = EncryptedRecordMessage.create(
        sender=__actor, folder_uuid=folder.uuid, message=message
    )
    m.encrypt(user=__actor)
    m.save()


@use_case
def optimize_messages(__actor: RlcUser):
    messages_1 = EncryptedRecordMessage.objects.filter(
        folder_uuid=None, record__template__rlc_id=__actor.org_id
    )
    messages_2 = list(messages_1)
    for message in messages_2:
        message.put_in_folder(__actor)
    EncryptedRecordMessage.objects.bulk_update(
        messages_2, ["key", "enc_message", "folder_uuid"]
    )
