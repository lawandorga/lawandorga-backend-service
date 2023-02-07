from core.mail.api import schemas
from core.mail.models import MailUser
from core.mail.use_cases.group import (
    add_address_to_group,
    add_member_to_group,
    create_group_mail,
    delete_group_address,
    delete_group_mail,
    remove_member_from_group,
    set_group_address_as_default,
)
from core.seedwork.api_layer import Router

router = Router()


@router.post()
def command__create_group_mail(mail_user: MailUser, data: schemas.InputCreateGroupMail):
    create_group_mail(mail_user, data.localpart, data.domain)


@router.delete(url="<uuid:group>/")
def command__delete_group_mail(mail_user: MailUser, data: schemas.InputDeleteGroupMail):
    delete_group_mail(mail_user, data.group)


@router.post(url="<uuid:group>/add_member/")
def command__add_member_to_group_mail(
    mail_user: MailUser, data: schemas.InputAddMemberToGroupMail
):
    add_member_to_group(mail_user, data.group, data.member)


@router.post(
    url="<uuid:group>/remove_member/",
)
def command__remove_member_from_group_mail(
    mail_user: MailUser, data: schemas.InputRemoveMemberFromGroupMail
):
    remove_member_from_group(mail_user, data.group, data.member)


@router.post(url="<uuid:group>/add_address/")
def command__add_address_to_group(
    mail_user: MailUser, data: schemas.InputAddAddressToGroup
):
    add_address_to_group(mail_user, data.localpart, data.group, data.domain)


@router.post(
    url="<uuid:group>/set_default_address/",
)
def command__set_address_as_default(
    mail_user: MailUser, data: schemas.InputSetDefaultGroupAddress
):
    set_group_address_as_default(mail_user, data.address)


@router.post(url="<uuid:group>/delete_address/")
def command__delete_group_address(
    mail_user: MailUser, data: schemas.InputDeleteGroupAddress
):
    delete_group_address(mail_user, data.address)
