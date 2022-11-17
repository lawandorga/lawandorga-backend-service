from core.mail.api import schemas
from core.mail.models import MailUser
from core.mail.use_cases.domain import add_domain
from core.seedwork.api_layer import Router

router = Router()


@router.post(input_schema=schemas.InputAddDomain)
def command__add_domain(__actor: MailUser, data: schemas.InputAddDomain):
    add_domain(__actor, data.domain)
