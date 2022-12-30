from core.auth.models import RlcUser
from core.messages.use_cases.message import create_a_message, optimize_messages
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.post(input_schema=schemas.InputSendMessage)
def command__send_message(rlc_user: RlcUser, data: schemas.InputSendMessage):
    create_a_message(rlc_user, data.message, data.folder)


@router.post(url="optimize/")
def command__optimize(rlc_user: RlcUser):
    optimize_messages(rlc_user)
