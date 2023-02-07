from core.auth.models import UserProfile
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


@router.post()
def command__create_user(user: UserProfile):
    create_mail_user(user)


@router.post(url="<uuid:user>/add_address/")
def command__create_address(mail_user: MailUser, data: schemas.InputCreateAddress):
    create_address(mail_user, data.localpart, data.user, data.domain)


@router.delete(
    url="<uuid:user>/delete_address/<uuid:address>/",
)
def command__delete_address(mail_user: MailUser, data: schemas.InputDeleteAddress):
    delete_address(mail_user, data.address)


@router.post(
    url="<uuid:user>/set_default_address/<uuid:address>/",
)
def command__set_address_as_default(
    mail_user: MailUser, data: schemas.InputSetDefaultAddress
):
    set_address_as_default(mail_user, data.address)


@router.post(url="regenerate_password/", output_schema=schemas.OutputPassword)
def command__regenerate_password(mail_user: MailUser):
    password = mail_user.generate_random_password()
    mail_user.set_password(password)
    mail_user.save()
    return {"password": password}
