from core.auth.models import RlcUser, UserProfile
from core.mail.api import schemas
from core.mail.models import MailUser
from core.mail.use_cases.user import (
    create_address,
    create_mail_user,
    delete_address,
    set_address_as_default,
)
from core.seedwork.api_layer import Router

router = Router()


@router.get(url="self/", output_schema=schemas.OutputMailUser)
def query__user(user: RlcUser):
    if hasattr(user, "mail_user"):
        return user.mail_user

    return {"email": None, "id": None}


@router.post()
def command__create_user(user: UserProfile):
    create_mail_user(user)


@router.post(url="<uuid:user>/add_alias/", input_schema=schemas.InputCreateAlias)
def command__create_alias(mail_user: MailUser, data: schemas.InputCreateAlias):
    create_address(mail_user, data.localpart, data.user, data.domain)


@router.delete(url="delete_alias/<uuid:alias>/", input_schema=schemas.InputDeleteAlias)
def command__delete_alias(mail_user: MailUser, data: schemas.InputDeleteAlias):
    delete_address(mail_user, data.alias)


@router.post(
    url="set_default_alias/<uuid:alias>/", input_schema=schemas.InputSetDefaultAlias
)
def command__set_alias_as_default(
    mail_user: MailUser, data: schemas.InputSetDefaultAlias
):
    set_address_as_default(mail_user, data.alias)
