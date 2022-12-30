from core.auth.models import RlcUser
from core.seedwork.api_layer import Router

from ..models import EncryptedRecordMessage
from . import schemas

router = Router()


@router.get(
    url="<uuid:folder>/",
    input_schema=schemas.InputGetMessages,
    output_schema=list[schemas.OutputMessage],
)
def query__get_messages(rlc_user: RlcUser, data: schemas.InputGetMessages):
    messages_1 = EncryptedRecordMessage.objects.filter(
        folder_uuid=data.folder
    ).select_related("sender")
    messages_2 = list(messages_1)
    messages_3 = [message.decrypt(rlc_user) for message in messages_2]
    return messages_3
