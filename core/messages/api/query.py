from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from core.auth.models import OrgUser
from core.messages.models import EncryptedRecordMessage
from core.seedwork.api_layer import Router


class InputGetMessages(BaseModel):
    folder: UUID


class OutputMessage(BaseModel):
    id: int
    message: str
    created: datetime
    sender_name: str

    model_config = ConfigDict(from_attributes=True)


router = Router()


@router.get(
    url="<uuid:folder>/",
    output_schema=list[OutputMessage],
)
def query__get_messages(rlc_user: OrgUser, data: InputGetMessages):
    messages_1 = EncryptedRecordMessage.objects.filter(
        folder_uuid=data.folder
    ).select_related("sender")
    messages_2 = list(messages_1)
    messages_3 = [message.decrypt(rlc_user) for message in messages_2]
    return messages_3
