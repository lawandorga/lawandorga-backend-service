from core.auth.models.org_user import OrgUser
from core.messages.models.message import EncryptedRecordMessage
from core.seedwork.use_case_layer import finder_function


@finder_function
def get_message_by_uuid(__actor: OrgUser, message_id: int):
    return EncryptedRecordMessage.objects.get(pk=message_id, org_id=__actor.org_id)
