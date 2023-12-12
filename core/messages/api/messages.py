from core.auth.models import OrgUser
from core.messages.use_cases.message import create_a_message, optimize_messages
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.post()
def command__send_message(rlc_user: OrgUser, data: schemas.InputSendMessage):
    create_a_message(rlc_user, data.message, data.folder)


@router.post(url="optimize/")
def command__optimize(rlc_user: OrgUser):
    optimize_messages(rlc_user)
