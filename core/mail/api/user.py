from core.auth.models import RlcUser, UserProfile
from core.mail.api import schemas
from core.mail.models import MailUser
from core.mail.use_cases.user import (
    create_alias,
    create_mail_user,
    delete_alias,
    set_alias_as_default,
)
from core.seedwork.api_layer import Router

router = Router()


@router.get()
def query__users(__actor: RlcUser):
    pass


@router.post()
def command__create_user(__actor: UserProfile):
    create_mail_user(__actor)


@router.post(input_schema=schemas.InputCreateAlias)
def command__create_alias(__actor: MailUser, data: schemas.InputCreateAlias):
    create_alias(__actor, data.localpart, data.domain)


@router.delete(input_schema=schemas.InputDeleteAlias)
def command__delete_alias(__actor: MailUser, data: schemas.InputDeleteAlias):
    delete_alias(__actor, data.id)


@router.post(input_schema=schemas.InputSetDefaultAlias)
def command__set_alias_as_default(
    __actor: MailUser, data: schemas.InputSetDefaultAlias
):
    set_alias_as_default(__actor, data.id)
